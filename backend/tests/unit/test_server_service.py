import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ExternalServiceError, NotFoundError
from app.models.server import Server, ServerType, Environment
from app.repositories.server_repository import ServerRepository
from app.schemas.server import ServerCreate, ServerUpdate
from app.services.server_service import ServerService
from app.services.ssh_manager import SSHManager


def make_server() -> MagicMock:
    s = MagicMock(spec=Server)
    s.id = uuid.uuid4()
    s.name = "prod1"
    s.host = "10.0.0.1"
    s.port = 22
    s.ssh_user = "ubuntu"
    s.ssh_password_encrypted = None
    s.ssh_key_encrypted = None
    s.server_type = ServerType.PRODUCTION
    s.environment = Environment.PRODUCTION
    s.monitoring_interval = 60
    s.is_active = True
    s.last_seen = None
    s.created_by = None
    s.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return s


@pytest.fixture
def server_repo():
    return AsyncMock(spec=ServerRepository)


@pytest.fixture
def ssh():
    m = MagicMock(spec=SSHManager)
    m.test_connection.return_value = True
    return m


@pytest.fixture
def svc(server_repo, ssh):
    return ServerService(server_repo, manager=ssh)


@pytest.mark.asyncio
async def test_create_server_success(svc, server_repo, ssh):
    server = make_server()
    server_repo.create.return_value = server

    data = ServerCreate(name="prod1", host="10.0.0.1", ssh_user="ubuntu", ssh_password="pass")
    result = await svc.create(data, validate_ssh=True)
    assert result is server
    ssh.test_connection.assert_called_once()


@pytest.mark.asyncio
async def test_create_server_ssh_fails(svc, server_repo, ssh):
    ssh.test_connection.return_value = False

    data = ServerCreate(name="prod1", host="10.0.0.1", ssh_user="ubuntu", ssh_password="pass")
    with pytest.raises(ExternalServiceError):
        await svc.create(data, validate_ssh=True)


@pytest.mark.asyncio
async def test_get_server_not_found(svc, server_repo):
    server_repo.get_by_id.return_value = None
    with pytest.raises(NotFoundError):
        await svc.get(uuid.uuid4())


@pytest.mark.asyncio
async def test_delete_server(svc, server_repo):
    server = make_server()
    server_repo.get_by_id.return_value = server
    await svc.delete(server.id)
    server_repo.delete.assert_called_once_with(server)


@pytest.mark.asyncio
async def test_list_servers(svc, server_repo):
    servers = [make_server(), make_server()]
    server_repo.list.return_value = servers
    result = await svc.list()
    assert len(result) == 2
