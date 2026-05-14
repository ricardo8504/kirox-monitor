import uuid
from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metric import Metric, MetricType, OdooMetric, PgMetric


class MetricRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest_all(self, server_id: uuid.UUID) -> dict[str, Metric]:
        stmt = select(Metric).from_statement(
            text(
                "SELECT DISTINCT ON (metric_type) * FROM metrics"
                " WHERE server_id = :sid ORDER BY metric_type, timestamp DESC"
            ).bindparams(sid=server_id)
        )
        result = await self._session.execute(stmt)
        return {m.metric_type: m for m in result.scalars().all()}

    async def insert_batch(self, metrics: list[Metric]) -> None:
        for m in metrics:
            self._session.add(m)
        await self._session.flush()

    async def get_latest(self, server_id: uuid.UUID, metric_type: MetricType) -> Metric | None:
        result = await self._session.execute(
            select(Metric)
            .where(Metric.server_id == server_id, Metric.metric_type == metric_type)
            .order_by(Metric.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_range(
        self,
        server_id: uuid.UUID,
        metric_type: MetricType,
        from_ts: datetime,
        to_ts: datetime,
    ) -> Sequence[Metric]:
        result = await self._session.execute(
            select(Metric)
            .where(
                Metric.server_id == server_id,
                Metric.metric_type == metric_type,
                Metric.timestamp >= from_ts,
                Metric.timestamp <= to_ts,
            )
            .order_by(Metric.timestamp.asc())
        )
        return result.scalars().all()

    async def insert_odoo(self, m: OdooMetric) -> OdooMetric:
        self._session.add(m)
        await self._session.flush()
        return m

    async def get_latest_odoo(self, server_id: uuid.UUID) -> OdooMetric | None:
        result = await self._session.execute(
            select(OdooMetric)
            .where(OdooMetric.server_id == server_id)
            .order_by(OdooMetric.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def insert_pg(self, m: PgMetric) -> PgMetric:
        self._session.add(m)
        await self._session.flush()
        return m

    async def get_latest_pg(self, server_id: uuid.UUID) -> PgMetric | None:
        result = await self._session.execute(
            select(PgMetric)
            .where(PgMetric.server_id == server_id)
            .order_by(PgMetric.timestamp.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_odoo_range(
        self,
        server_id: uuid.UUID,
        from_ts: datetime,
        to_ts: datetime,
    ) -> Sequence[OdooMetric]:
        result = await self._session.execute(
            select(OdooMetric)
            .where(
                OdooMetric.server_id == server_id,
                OdooMetric.timestamp >= from_ts,
                OdooMetric.timestamp <= to_ts,
            )
            .order_by(OdooMetric.timestamp.asc())
        )
        return result.scalars().all()

    async def get_pg_range(
        self,
        server_id: uuid.UUID,
        from_ts: datetime,
        to_ts: datetime,
    ) -> Sequence[PgMetric]:
        result = await self._session.execute(
            select(PgMetric)
            .where(
                PgMetric.server_id == server_id,
                PgMetric.timestamp >= from_ts,
                PgMetric.timestamp <= to_ts,
            )
            .order_by(PgMetric.timestamp.asc())
        )
        return result.scalars().all()
