import asyncio
import uuid
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging import get_logger
from app.repositories.metric_repository import MetricRepository
from app.repositories.server_repository import ServerRepository
from app.services.monitoring_orchestrator import MonitoringOrchestrator
from app.services.ssh_manager import ssh_manager
from app.workers.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(name="app.workers.tasks.collect_metrics", bind=True, max_retries=2)
def collect_metrics(self, server_id: str) -> dict:  # type: ignore[no-untyped-def]
    async def _run() -> dict:
        async with AsyncSessionLocal() as session:
            orchestrator = MonitoringOrchestrator(
                server_repo=ServerRepository(session),
                metric_repo=MetricRepository(session),
                ssh=ssh_manager,
            )
            success = await orchestrator.collect(uuid.UUID(server_id))
            if success:
                await session.commit()
            return {"server_id": server_id, "success": success}

    try:
        return asyncio.run(_run())
    except Exception as exc:
        logger.error("collect_metrics_failed", server_id=server_id, error=str(exc))
        raise self.retry(exc=exc, countdown=30) from exc


@celery_app.task(name="app.workers.tasks.collect_all_servers")
def collect_all_servers() -> dict:
    async def _get_active_ids() -> list[str]:
        async with AsyncSessionLocal() as session:
            repo = ServerRepository(session)
            servers = await repo.list(is_active=True)
            return [str(s.id) for s in servers]

    server_ids = asyncio.run(_get_active_ids())
    for sid in server_ids:
        collect_metrics.delay(sid)
    logger.info("collect_all_dispatched", count=len(server_ids))
    return {"dispatched": len(server_ids)}


@celery_app.task(name="app.workers.tasks.cleanup_old_metrics")
def cleanup_old_metrics() -> dict:
    from sqlalchemy import delete

    from app.models.metric import Metric, OdooMetric, PgMetric

    async def _cleanup() -> None:
        cutoff = datetime.now(UTC) - timedelta(days=settings.metric_retention_days)
        async with AsyncSessionLocal() as session:
            for model in (Metric, OdooMetric, PgMetric):
                await session.execute(delete(model).where(model.timestamp < cutoff))
            await session.commit()

    asyncio.run(_cleanup())
    logger.info("cleanup_old_metrics_done", retention_days=settings.metric_retention_days)
    return {"status": "ok"}
