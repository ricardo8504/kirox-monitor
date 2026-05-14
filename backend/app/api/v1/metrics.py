import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.metric import MetricType
from app.models.user import UserRole
from app.repositories.metric_repository import MetricRepository
from app.schemas.metric import MetricResponse, OdooMetricResponse, PgMetricResponse

router = APIRouter(tags=["metrics"])

_any_role = require_roles(UserRole.ADMIN, UserRole.OPERATOR, UserRole.READONLY)


def get_metric_repo(db: AsyncSession = Depends(get_db)) -> MetricRepository:
    return MetricRepository(db)


@router.get(
    "/servers/{server_id}/metrics/latest",
    response_model=dict[str, MetricResponse | None],
    dependencies=[Depends(_any_role)],
)
async def get_latest_metrics(
    server_id: uuid.UUID,
    repo: MetricRepository = Depends(get_metric_repo),
) -> dict:
    latest = await repo.get_latest_all(server_id)
    return {
        mtype.value: MetricResponse.model_validate(latest[mtype.value])
        if mtype.value in latest else None
        for mtype in MetricType
    }


@router.get(
    "/servers/{server_id}/metrics/history",
    response_model=list[MetricResponse],
    dependencies=[Depends(_any_role)],
)
async def get_metric_history(
    server_id: uuid.UUID,
    metric: MetricType = Query(...),
    from_ts: datetime = Query(..., alias="from"),
    to_ts: datetime = Query(..., alias="to"),
    repo: MetricRepository = Depends(get_metric_repo),
) -> list[MetricResponse]:
    items = await repo.get_range(server_id, metric, from_ts, to_ts)
    return [MetricResponse.model_validate(m) for m in items]


@router.get(
    "/servers/{server_id}/metrics/odoo/latest",
    response_model=OdooMetricResponse | None,
    dependencies=[Depends(_any_role)],
)
async def get_latest_odoo(
    server_id: uuid.UUID,
    repo: MetricRepository = Depends(get_metric_repo),
) -> OdooMetricResponse | None:
    m = await repo.get_latest_odoo(server_id)
    return OdooMetricResponse.model_validate(m) if m else None


@router.get(
    "/servers/{server_id}/metrics/pg/latest",
    response_model=PgMetricResponse | None,
    dependencies=[Depends(_any_role)],
)
async def get_latest_pg(
    server_id: uuid.UUID,
    repo: MetricRepository = Depends(get_metric_repo),
) -> PgMetricResponse | None:
    m = await repo.get_latest_pg(server_id)
    return PgMetricResponse.model_validate(m) if m else None


@router.get(
    "/servers/{server_id}/metrics/odoo/history",
    response_model=list[OdooMetricResponse],
    dependencies=[Depends(_any_role)],
)
async def get_odoo_history(
    server_id: uuid.UUID,
    from_ts: datetime = Query(..., alias="from"),
    to_ts: datetime = Query(..., alias="to"),
    repo: MetricRepository = Depends(get_metric_repo),
) -> list[OdooMetricResponse]:
    items = await repo.get_odoo_range(server_id, from_ts, to_ts)
    return [OdooMetricResponse.model_validate(m) for m in items]


@router.get(
    "/servers/{server_id}/metrics/pg/history",
    response_model=list[PgMetricResponse],
    dependencies=[Depends(_any_role)],
)
async def get_pg_history(
    server_id: uuid.UUID,
    from_ts: datetime = Query(..., alias="from"),
    to_ts: datetime = Query(..., alias="to"),
    repo: MetricRepository = Depends(get_metric_repo),
) -> list[PgMetricResponse]:
    items = await repo.get_pg_range(server_id, from_ts, to_ts)
    return [PgMetricResponse.model_validate(m) for m in items]
