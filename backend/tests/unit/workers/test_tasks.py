import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.server import Server


def make_active_server() -> MagicMock:
    s = MagicMock(spec=Server)
    s.id = uuid.uuid4()
    s.is_active = True
    return s


def test_collect_metrics_task_calls_orchestrator():
    server_id = str(uuid.uuid4())
    expected = {"server_id": server_id, "success": True}

    with patch("app.workers.tasks.asyncio") as mock_asyncio:
        mock_asyncio.run.return_value = expected

        from app.workers.tasks import collect_metrics
        result = collect_metrics.run(server_id)

    assert result["success"] is True
    assert result["server_id"] == server_id
    mock_asyncio.run.assert_called_once()


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
