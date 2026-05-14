import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.alert import AlertCondition, AlertSeverity, ChannelType
from app.models.metric import MetricType


class AlertRuleCreate(BaseModel):
    server_id: uuid.UUID
    metric_type: MetricType
    condition: AlertCondition
    threshold: float
    severity: AlertSeverity
    cooldown_minutes: int = 15


class AlertRuleUpdate(BaseModel):
    threshold: float | None = None
    severity: AlertSeverity | None = None
    enabled: bool | None = None
    cooldown_minutes: int | None = None


class AlertRuleResponse(BaseModel):
    id: uuid.UUID
    server_id: uuid.UUID
    metric_type: str
    condition: AlertCondition
    threshold: float
    severity: AlertSeverity
    enabled: bool
    cooldown_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertEventResponse(BaseModel):
    id: uuid.UUID
    rule_id: uuid.UUID
    server_id: uuid.UUID
    message: str
    severity: AlertSeverity
    metric_value: float
    notified_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationChannelCreate(BaseModel):
    channel_type: ChannelType
    name: str
    config: dict


class NotificationChannelResponse(BaseModel):
    id: uuid.UUID
    channel_type: ChannelType
    name: str
    enabled: bool
    user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
