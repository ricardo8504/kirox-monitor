import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.models.alert import AlertCondition, AlertEvent, AlertRule, AlertSeverity
from app.repositories.alert_repository import AlertEventRepository, AlertRuleRepository
from app.services.alert_engine import AlertEngine, _evaluate_condition


# --- Pure evaluation logic ---

def test_greater_than_true():
    assert _evaluate_condition(AlertCondition.GREATER_THAN, 95.0, 90.0) is True


def test_greater_than_false():
    assert _evaluate_condition(AlertCondition.GREATER_THAN, 80.0, 90.0) is False


def test_less_than_true():
    assert _evaluate_condition(AlertCondition.LESS_THAN, 10.0, 20.0) is True


def test_less_than_false():
    assert _evaluate_condition(AlertCondition.LESS_THAN, 30.0, 20.0) is False


def test_equals_true():
    assert _evaluate_condition(AlertCondition.EQUALS, 100.0, 100.0) is True


def test_equals_false():
    assert _evaluate_condition(AlertCondition.EQUALS, 99.9, 100.0) is False


# --- AlertEngine ---

def make_rule(condition=AlertCondition.GREATER_THAN, threshold=90.0) -> MagicMock:
    r = MagicMock(spec=AlertRule)
    r.id = uuid.uuid4()
    r.server_id = uuid.uuid4()
    r.metric_type = "CPU_USAGE"
    r.condition = condition
    r.threshold = threshold
    r.severity = AlertSeverity.WARNING
    r.cooldown_minutes = 15
    r.enabled = True
    return r


@pytest.fixture
def rule_repo():
    return AsyncMock(spec=AlertRuleRepository)


@pytest.fixture
def event_repo():
    return AsyncMock(spec=AlertEventRepository)


@pytest.fixture
def engine(rule_repo, event_repo):
    return AlertEngine(rule_repo, event_repo, redis_url="redis://localhost:6379/0")


@pytest.mark.asyncio
async def test_evaluate_rule_fires(engine, rule_repo, event_repo):
    rule = make_rule()
    rule_repo.list_by_server.return_value = [rule]
    created_event = MagicMock(spec=AlertEvent)
    event_repo.create.return_value = created_event

    with patch.object(engine, "_is_in_cooldown", return_value=False), \
         patch.object(engine, "_set_cooldown"):
        fired = await engine.evaluate_rules(rule.server_id, {"CPU_USAGE": 95.0})

    assert len(fired) == 1
    assert fired[0] is created_event


@pytest.mark.asyncio
async def test_evaluate_rule_below_threshold(engine, rule_repo, event_repo):
    rule = make_rule()
    rule_repo.list_by_server.return_value = [rule]

    with patch.object(engine, "_is_in_cooldown", return_value=False):
        fired = await engine.evaluate_rules(rule.server_id, {"CPU_USAGE": 80.0})

    assert len(fired) == 0
    event_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_evaluate_rule_cooldown_skips(engine, rule_repo, event_repo):
    rule = make_rule()
    rule_repo.list_by_server.return_value = [rule]

    with patch.object(engine, "_is_in_cooldown", return_value=True):
        fired = await engine.evaluate_rules(rule.server_id, {"CPU_USAGE": 95.0})

    assert len(fired) == 0
    event_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_evaluate_missing_metric_skips(engine, rule_repo, event_repo):
    rule = make_rule()
    rule_repo.list_by_server.return_value = [rule]

    with patch.object(engine, "_is_in_cooldown", return_value=False):
        fired = await engine.evaluate_rules(rule.server_id, {"RAM_USAGE": 80.0})

    assert len(fired) == 0
