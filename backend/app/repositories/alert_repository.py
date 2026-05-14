import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import AlertEvent, AlertRule, NotificationChannel


class AlertRuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, rule: AlertRule) -> AlertRule:
        self._session.add(rule)
        await self._session.flush()
        await self._session.refresh(rule)
        return rule

    async def get_by_id(self, rule_id: uuid.UUID) -> AlertRule | None:
        result = await self._session.execute(select(AlertRule).where(AlertRule.id == rule_id))
        return result.scalar_one_or_none()

    async def list_by_server(self, server_id: uuid.UUID) -> Sequence[AlertRule]:
        result = await self._session.execute(
            select(AlertRule).where(AlertRule.server_id == server_id, AlertRule.enabled == True)  # noqa: E712
        )
        return result.scalars().all()

    async def update(self, rule: AlertRule) -> AlertRule:
        await self._session.flush()
        await self._session.refresh(rule)
        return rule

    async def delete(self, rule: AlertRule) -> None:
        await self._session.delete(rule)
        await self._session.flush()


class AlertEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, event: AlertEvent) -> AlertEvent:
        self._session.add(event)
        await self._session.flush()
        await self._session.refresh(event)
        return event

    async def list_recent(self, limit: int = 100) -> Sequence[AlertEvent]:
        result = await self._session.execute(
            select(AlertEvent).order_by(AlertEvent.created_at.desc()).limit(limit)
        )
        return result.scalars().all()

    async def get_by_id(self, event_id: uuid.UUID) -> AlertEvent | None:
        result = await self._session.execute(select(AlertEvent).where(AlertEvent.id == event_id))
        return result.scalar_one_or_none()

    async def update(self, event: AlertEvent) -> AlertEvent:
        await self._session.flush()
        return event


class NotificationChannelRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, channel: NotificationChannel) -> NotificationChannel:
        self._session.add(channel)
        await self._session.flush()
        await self._session.refresh(channel)
        return channel

    async def list_by_user(self, user_id: uuid.UUID) -> Sequence[NotificationChannel]:
        result = await self._session.execute(
            select(NotificationChannel).where(NotificationChannel.user_id == user_id)
        )
        return result.scalars().all()

    async def get_by_id(self, channel_id: uuid.UUID) -> NotificationChannel | None:
        result = await self._session.execute(
            select(NotificationChannel).where(NotificationChannel.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, channel: NotificationChannel) -> None:
        await self._session.delete(channel)
        await self._session.flush()
