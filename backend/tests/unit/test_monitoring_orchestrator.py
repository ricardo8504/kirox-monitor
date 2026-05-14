import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repositories.metric_repository import MetricRepository
from app.repositories.server_repository import ServerRepository
from app.services.monitoring_orchestrator import MonitoringOrchestrator
from app.services.ssh_manager import SSHManager, CommandResult
from app.models.server import Server, ServerType, Environment


def make_server(active: bool = True) -> MagicMock:
    s = MagicMock(spec=Server)
    s.id = uuid.uuid4()
    s.host = "10.0.0.1"
    s.port = 22
    s.ssh_user = "ubuntu"
    s.ssh_password_encrypted = None
    s.ssh_key_encrypted = None
    s.is_active = active
    return s


@pytest.fixture
def server_repo():
    return AsyncMock(spec=ServerRepository)


@pytest.fixture
def metric_repo():
    repo = AsyncMock(spec=MetricRepository)
    repo.insert_batch.return_value = None
    repo.insert_odoo.return_value = None
    repo.insert_pg.return_value = None
    return repo


@pytest.fixture
def ssh():
    m = MagicMock(spec=SSHManager)
    m.execute_command.return_value = CommandResult(stdout="", stderr="", exit_code=0)
    return m


@pytest.fixture
def orchestrator(server_repo, metric_repo, ssh):
    return MonitoringOrchestrator(server_repo, metric_repo, ssh)


@pytest.mark.asyncio
async def test_collect_inactive_server(orchestrator, server_repo):
    server = make_server(active=False)
    server_repo.get_by_id.return_value = server
    result = await orchestrator.collect(server.id)
    assert result is False


@pytest.mark.asyncio
async def test_collect_server_not_found(orchestrator, server_repo):
    server_repo.get_by_id.return_value = None
    result = await orchestrator.collect(uuid.uuid4())
    assert result is False


@pytest.mark.asyncio
async def test_collect_success(orchestrator, server_repo, metric_repo, ssh):
    server = make_server()
    server_repo.get_by_id.return_value = server
    ssh.execute_command.return_value = CommandResult(stdout="", stderr="", exit_code=0)

    result = await orchestrator.collect(server.id)
    assert result is True
    metric_repo.insert_batch.assert_called_once()
    metric_repo.insert_odoo.assert_called_once()
    metric_repo.insert_pg.assert_called_once()


@pytest.mark.asyncio
async def test_collect_ssh_errors_per_command_still_succeeds(orchestrator, server_repo, metric_repo, ssh):
    from app.core.exceptions import ExternalServiceError
    server = make_server()
    server_repo.get_by_id.return_value = server
    # Per-command SSH errors are caught inside _run_commands → empty outputs → zero metrics saved
    ssh.execute_command.side_effect = ExternalServiceError("SSH", "timeout")

    result = await orchestrator.collect(server.id)
    # Still returns True — server was processed (with empty metrics)
    assert result is True
    metric_repo.insert_batch.assert_called_once()
    metric_repo.insert_odoo.assert_called_once()
    metric_repo.insert_pg.assert_called_once()
