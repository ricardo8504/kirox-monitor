import json
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_audit_repo, get_current_user, require_roles
from app.core.encryption import encrypt
from app.core.exceptions import ForbiddenError, NotFoundError
from app.models.alert import AlertRule, NotificationChannel
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.repositories.alert_repository import (
    AlertEventRepository,
    AlertRuleRepository,
    NotificationChannelRepository,
)
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.alert import (
    AlertEventResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    AlertRuleUpdate,
    NotificationChannelCreate,
    NotificationChannelResponse,
)

router = APIRouter(tags=["alerts"])

_any_role = require_roles(UserRole.ADMIN, UserRole.OPERATOR, UserRole.READONLY)
_write_role = require_roles(UserRole.ADMIN, UserRole.OPERATOR)
_admin = require_roles(UserRole.ADMIN)


def _rule_repo(db: AsyncSession = Depends(get_db)) -> AlertRuleRepository:
    return AlertRuleRepository(db)


def _event_repo(db: AsyncSession = Depends(get_db)) -> AlertEventRepository:
    return AlertEventRepository(db)


def _channel_repo(db: AsyncSession = Depends(get_db)) -> NotificationChannelRepository:
    return NotificationChannelRepository(db)


# --- Alert Rules ---

@router.post("/alerts/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(_write_role)])
async def create_rule(
    request: Request,
    body: AlertRuleCreate,
    user: User = Depends(get_current_user),
    repo: AlertRuleRepository = Depends(_rule_repo),
    audit: AuditLogRepository = Depends(get_audit_repo),
) -> AlertRuleResponse:
    rule = await repo.create(AlertRule(
        server_id=body.server_id,
        metric_type=body.metric_type.value,
        condition=body.condition,
        threshold=body.threshold,
        severity=body.severity,
        cooldown_minutes=body.cooldown_minutes,
        created_by=user.id,
    ))
    await audit.create(AuditLog(
        user_id=user.id, action="CREATE", resource="alert_rule", resource_id=str(rule.id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    ))
    return AlertRuleResponse.model_validate(rule)


@router.get(
    "/alerts/rules", response_model=list[AlertRuleResponse], dependencies=[Depends(_any_role)]
)
async def list_rules(
    server_id: uuid.UUID | None = None,
    repo: AlertRuleRepository = Depends(_rule_repo),
) -> list[AlertRuleResponse]:
    if server_id:
        items = await repo.list_by_server(server_id)
    else:
        items = []
    return [AlertRuleResponse.model_validate(r) for r in items]


@router.put("/alerts/rules/{rule_id}", response_model=AlertRuleResponse,
            dependencies=[Depends(_write_role)])
async def update_rule(
    request: Request,
    rule_id: uuid.UUID,
    body: AlertRuleUpdate,
    user: User = Depends(get_current_user),
    repo: AlertRuleRepository = Depends(_rule_repo),
    audit: AuditLogRepository = Depends(get_audit_repo),
) -> AlertRuleResponse:
    rule = await repo.get_by_id(rule_id)
    if not rule:
        raise NotFoundError("AlertRule", rule_id)
    for field in ("threshold", "severity", "enabled", "cooldown_minutes"):
        val = getattr(body, field, None)
        if val is not None:
            setattr(rule, field, val)
    rule = await repo.update(rule)
    await audit.create(AuditLog(
        user_id=user.id, action="UPDATE", resource="alert_rule", resource_id=str(rule_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    ))
    return AlertRuleResponse.model_validate(rule)


@router.delete("/alerts/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(_write_role)])
async def delete_rule(
    request: Request,
    rule_id: uuid.UUID,
    user: User = Depends(get_current_user),
    repo: AlertRuleRepository = Depends(_rule_repo),
    audit: AuditLogRepository = Depends(get_audit_repo),
) -> None:
    rule = await repo.get_by_id(rule_id)
    if not rule:
        raise NotFoundError("AlertRule", rule_id)
    await repo.delete(rule)
    await audit.create(AuditLog(
        user_id=user.id, action="DELETE", resource="alert_rule", resource_id=str(rule_id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    ))


# --- Alert Events ---

@router.get(
    "/alerts/events", response_model=list[AlertEventResponse], dependencies=[Depends(_any_role)]
)
async def list_events(
    limit: int = 100,
    repo: AlertEventRepository = Depends(_event_repo),
) -> list[AlertEventResponse]:
    items = await repo.list_recent(limit=limit)
    return [AlertEventResponse.model_validate(e) for e in items]


@router.post("/alerts/events/{event_id}/resolve", response_model=AlertEventResponse,
             dependencies=[Depends(_write_role)])
async def resolve_event(
    event_id: uuid.UUID,
    repo: AlertEventRepository = Depends(_event_repo),
) -> AlertEventResponse:
    event = await repo.get_by_id(event_id)
    if not event:
        raise NotFoundError("AlertEvent", event_id)
    event.resolved_at = datetime.now(UTC)
    event = await repo.update(event)
    return AlertEventResponse.model_validate(event)


# --- Notification Channels ---

@router.post("/notifications/channels", response_model=NotificationChannelResponse,
             status_code=status.HTTP_201_CREATED)
async def create_channel(
    body: NotificationChannelCreate,
    user: User = Depends(get_current_user),
    repo: NotificationChannelRepository = Depends(_channel_repo),
) -> NotificationChannelResponse:
    channel = await repo.create(NotificationChannel(
        channel_type=body.channel_type,
        name=body.name,
        config_encrypted=encrypt(json.dumps(body.config)),
        user_id=user.id,
    ))
    return NotificationChannelResponse.model_validate(channel)


@router.get("/notifications/channels", response_model=list[NotificationChannelResponse])
async def list_channels(
    user: User = Depends(get_current_user),
    repo: NotificationChannelRepository = Depends(_channel_repo),
) -> list[NotificationChannelResponse]:
    items = await repo.list_by_user(user.id)
    return [NotificationChannelResponse.model_validate(c) for c in items]


@router.delete("/notifications/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: uuid.UUID,
    user: User = Depends(get_current_user),
    repo: NotificationChannelRepository = Depends(_channel_repo),
) -> None:
    channel = await repo.get_by_id(channel_id)
    if not channel:
        raise NotFoundError("NotificationChannel", channel_id)
    if channel.user_id != user.id:
        raise ForbiddenError("Cannot delete another user's channel")
    await repo.delete(channel)
