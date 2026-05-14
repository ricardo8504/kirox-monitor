import uuid

import redis.asyncio as aioredis

from app.core.config import settings
from app.core.logging import get_logger
from app.models.alert import AlertCondition, AlertEvent, AlertRule
from app.repositories.alert_repository import AlertEventRepository, AlertRuleRepository

logger = get_logger(__name__)

_COOLDOWN_KEY = "alert_cooldown:{rule_id}"


def _evaluate_condition(condition: AlertCondition, value: float, threshold: float) -> bool:
    if condition == AlertCondition.GREATER_THAN:
        return value > threshold
    if condition == AlertCondition.LESS_THAN:
        return value < threshold
    if condition == AlertCondition.EQUALS:
        return abs(value - threshold) < 1e-9
    return False


class AlertEngine:
    def __init__(
        self,
        rule_repo: AlertRuleRepository,
        event_repo: AlertEventRepository,
        redis_url: str | None = None,
    ) -> None:
        self._rules = rule_repo
        self._events = event_repo
        self._redis = aioredis.from_url(redis_url or settings.redis_url)

    async def _is_in_cooldown(self, rule_id: uuid.UUID) -> bool:
        try:
            key = _COOLDOWN_KEY.format(rule_id=rule_id)
            return await self._redis.get(key) is not None
        except Exception:
            return False

    async def _set_cooldown(self, rule: AlertRule) -> None:
        try:
            key = _COOLDOWN_KEY.format(rule_id=rule.id)
            await self._redis.set(key, "1", ex=rule.cooldown_minutes * 60)
        except Exception:  # noqa: S110
            pass

    async def evaluate_rules(
        self, server_id: uuid.UUID, metrics: dict[str, float]
    ) -> list[AlertEvent]:
        rules = await self._rules.list_by_server(server_id)
        fired: list[AlertEvent] = []

        for rule in rules:
            value = metrics.get(rule.metric_type)
            if value is None:
                continue

            if not _evaluate_condition(rule.condition, value, rule.threshold):
                continue

            if await self._is_in_cooldown(rule.id):
                logger.info("alert_in_cooldown", rule_id=str(rule.id))
                continue

            event = await self._events.create(AlertEvent(
                rule_id=rule.id,
                server_id=server_id,
                severity=rule.severity,
                metric_value=value,
                message=(
                    f"Metric {rule.metric_type} is {value} "
                    f"({rule.condition} {rule.threshold})"
                ),
            ))
            await self._set_cooldown(rule)
            fired.append(event)

        return fired
