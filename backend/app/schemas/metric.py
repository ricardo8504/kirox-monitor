import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.metric import MetricType


class MetricResponse(BaseModel):
    id: uuid.UUID
    server_id: uuid.UUID
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    raw_data: dict | None = None

    model_config = {"from_attributes": True}


class OdooMetricResponse(BaseModel):
    id: uuid.UUID
    server_id: uuid.UUID
    workers_active: int
    processes_hung: int
    memory_mb: float
    cpu_percent: float
    response_time_ms: float | None
    requests_concurrent: int
    timestamp: datetime

    model_config = {"from_attributes": True}


class PgMetricResponse(BaseModel):
    id: uuid.UUID
    server_id: uuid.UUID
    connections_active: int
    slow_queries: int
    locks: int
    deadlocks: int
    db_size_mb: float
    timestamp: datetime

    model_config = {"from_attributes": True}
