import asyncio
import uuid
from datetime import UTC, datetime, timedelta

import redis as sync_redis
from sqlalchemy import delete

from app.core.config import settings
from app.core.database import CelerySessionLocal
from app.core.logging import get_logger
from app.models.metric import Metric, OdooMetric, PgMetric
from app.repositories.alert_repository import AlertEventRepository, AlertRuleRepository
from app.repositories.metric_repository import MetricRepository
from app.repositories.server_repository import ServerRepository
from app.services.alert_engine import AlertEngine
from app.services.monitoring_orchestrator import MonitoringOrchestrator
from app.services.ssh_manager import ssh_manager
from app.workers.celery_app import celery_app

logger = get_logger(__name__)

_COLLECT_LOCK_PREFIX = "celery:collect:lock:"
_COLLECT_LOCK_TTL = 55

_CIRCUIT_KEY = "circuit:open:{server_id}"
_CIRCUIT_FAIL_KEY = "circuit:failures:{server_id}"


def _is_circuit_open(r: "sync_redis.Redis", server_id: str) -> bool:
    return r.get(_CIRCUIT_KEY.format(server_id=server_id)) is not None


def _record_failure(r: "sync_redis.Redis", server_id: str) -> None:
    fail_key = _CIRCUIT_FAIL_KEY.format(server_id=server_id)
    failures = r.incr(fail_key)
    r.expire(fail_key, 3600)
    if failures >= settings.circuit_breaker_threshold:
        r.set(
            _CIRCUIT_KEY.format(server_id=server_id),
            "1",
            ex=settings.circuit_breaker_timeout,
        )
        logger.warning("circuit_breaker_opened", server_id=server_id, failures=failures)


def _record_success(r: "sync_redis.Redis", server_id: str) -> None:
    r.delete(_CIRCUIT_FAIL_KEY.format(server_id=server_id))
    r.delete(_CIRCUIT_KEY.format(server_id=server_id))


@celery_app.task(name="app.workers.tasks.collect_metrics", bind=True, max_retries=2)
def collect_metrics(self, server_id: str) -> dict:  # type: ignore[no-untyped-def]
    r = sync_redis.from_url(settings.redis_url)
    try:
        if _is_circuit_open(r, server_id):
            logger.info("collect_metrics_circuit_open", server_id=server_id)
            return {"server_id": server_id, "circuit_open": True}

        lock_key = f"{_COLLECT_LOCK_PREFIX}{server_id}"
        acquired = r.set(lock_key, "1", nx=True, ex=_COLLECT_LOCK_TTL)
        if not acquired:
            logger.info("collect_metrics_skipped_locked", server_id=server_id)
            return {"server_id": server_id, "skipped": True}

        async def _run() -> dict:
            async with CelerySessionLocal() as session:
                orchestrator = MonitoringOrchestrator(
                    server_repo=ServerRepository(session),
                    metric_repo=MetricRepository(session),
                    ssh=ssh_manager,
                    alert_engine=AlertEngine(
                        rule_repo=AlertRuleRepository(session),
                        event_repo=AlertEventRepository(session),
                    ),
                )
                success = await orchestrator.collect(uuid.UUID(server_id))
                if success:
                    await session.commit()
                return {"server_id": server_id, "success": success}

        try:
            result = asyncio.run(_run())
            _record_success(r, server_id)
            return result
        except Exception as exc:
            r.delete(lock_key)
            _record_failure(r, server_id)
            logger.error("collect_metrics_failed", server_id=server_id, error=str(exc))
            raise self.retry(exc=exc, countdown=30) from exc
    finally:
        r.close()


@celery_app.task(name="app.workers.tasks.collect_all_servers")
def collect_all_servers() -> dict:
    async def _get_active_ids() -> list[str]:
        async with CelerySessionLocal() as session:
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
    async def _cleanup() -> None:
        cutoff = datetime.now(UTC) - timedelta(days=settings.metric_retention_days)
        async with CelerySessionLocal() as session:
            for model in (Metric, OdooMetric, PgMetric):
                await session.execute(delete(model).where(model.timestamp < cutoff))
            await session.commit()

    asyncio.run(_cleanup())
    logger.info("cleanup_old_metrics_done", retention_days=settings.metric_retention_days)
    return {"status": "ok"}
