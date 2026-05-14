import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class MetricType(StrEnum):
    CPU_USAGE = "CPU_USAGE"
    RAM_USAGE = "RAM_USAGE"
    SWAP_USAGE = "SWAP_USAGE"
    DISK_USAGE = "DISK_USAGE"
    DISK_IO_READ = "DISK_IO_READ"
    DISK_IO_WRITE = "DISK_IO_WRITE"
    LOAD_AVG_1 = "LOAD_AVG_1"
    LOAD_AVG_5 = "LOAD_AVG_5"
    LOAD_AVG_15 = "LOAD_AVG_15"
    NETWORK_IN = "NETWORK_IN"
    NETWORK_OUT = "NETWORK_OUT"
    PROCESS_COUNT = "PROCESS_COUNT"
    CPU_TEMP = "CPU_TEMP"


class Metric(BaseModel):
    __tablename__ = "metrics"

    server_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    metric_type: Mapped[MetricType] = mapped_column(
        Enum(MetricType, name="metric_type"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_metrics_server_type_ts", "server_id", "metric_type", "timestamp"),
    )


class OdooMetric(BaseModel):
    __tablename__ = "odoo_metrics"

    server_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    workers_active: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    processes_hung: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    memory_mb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cpu_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    requests_concurrent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_odoo_metrics_server_ts", "server_id", "timestamp"),
    )


class PgMetric(BaseModel):
    __tablename__ = "pg_metrics"

    server_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    connections_active: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    slow_queries: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    locks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deadlocks: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    db_size_mb: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    __table_args__ = (
        Index("ix_pg_metrics_server_ts", "server_id", "timestamp"),
    )
