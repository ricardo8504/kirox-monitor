import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.server import Server


def make_active_server() -> MagicMock:
    s = MagicMock(spec=Server)
    s.id = uuid.uuid4()
    s.is_active = True
    return s


def _make_redis_mock(circuit_open: bool = False, lock_acquired: bool = True) -> MagicMock:
    r = MagicMock()
    r.get.return_value = b"1" if circuit_open else None
    r.set.return_value = True if lock_acquired else None
    r.incr.return_value = 1
    return r


def test_collect_metrics_task_calls_orchestrator():
    server_id = str(uuid.uuid4())
    expected = {"server_id": server_id, "success": True}

    with patch("app.workers.tasks.sync_redis.from_url") as mock_redis_cls, \
         patch("app.workers.tasks.asyncio") as mock_asyncio:

        mock_redis_cls.return_value = _make_redis_mock()
        mock_asyncio.run.return_value = expected

        from app.workers.tasks import collect_metrics
        result = collect_metrics.run(server_id)

    assert result["success"] is True
    assert result["server_id"] == server_id
    mock_asyncio.run.assert_called_once()


def test_collect_metrics_skips_when_locked():
    server_id = str(uuid.uuid4())

    with patch("app.workers.tasks.sync_redis.from_url") as mock_redis_cls, \
         patch("app.workers.tasks.asyncio") as mock_asyncio:

        mock_redis_cls.return_value = _make_redis_mock(lock_acquired=False)
        mock_asyncio.run.return_value = {"server_id": server_id, "success": True}

        from app.workers.tasks import collect_metrics
        result = collect_metrics.run(server_id)

    assert result["skipped"] is True
    mock_asyncio.run.assert_not_called()


def test_collect_metrics_skips_when_circuit_open():
    server_id = str(uuid.uuid4())

    with patch("app.workers.tasks.sync_redis.from_url") as mock_redis_cls, \
         patch("app.workers.tasks.asyncio") as mock_asyncio:

        mock_redis_cls.return_value = _make_redis_mock(circuit_open=True)

        from app.workers.tasks import collect_metrics
        result = collect_metrics.run(server_id)

    assert result["circuit_open"] is True
    mock_asyncio.run.assert_not_called()


def test_collect_all_servers_dispatches():
    servers = [make_active_server(), make_active_server()]
    server_ids = [str(s.id) for s in servers]

    with patch("app.workers.tasks.asyncio") as mock_asyncio, \
         patch("app.workers.tasks.collect_metrics") as mock_collect:

        mock_asyncio.run.return_value = server_ids
        mock_collect.delay = MagicMock()

        from app.workers.tasks import collect_all_servers
        result = collect_all_servers.run()

    assert result["dispatched"] == 2
    assert mock_collect.delay.call_count == 2
