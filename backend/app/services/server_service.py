import uuid

from app.core.encryption import decrypt, encrypt
from app.core.exceptions import ExternalServiceError, NotFoundError
from app.models.server import Server
from app.repositories.server_repository import ServerRepository
from app.schemas.server import ServerCreate, ServerUpdate
from app.services.ssh_manager import SSHManager, ssh_manager


class ServerService:
    def __init__(
        self,
        server_repo: ServerRepository,
        manager: SSHManager | None = None,
    ) -> None:
        self._servers = server_repo
        self._ssh = manager or ssh_manager

    def _encrypt_credentials(self, server: Server, data: ServerCreate | ServerUpdate) -> None:
        if hasattr(data, "ssh_password") and data.ssh_password:
            server.ssh_password_encrypted = encrypt(data.ssh_password)
        if hasattr(data, "ssh_key") and data.ssh_key:
            server.ssh_key_encrypted = encrypt(data.ssh_key)

    def _decrypt_for_ssh(self, server: Server) -> tuple[str | None, str | None]:
        password = decrypt(server.ssh_password_encrypted) if server.ssh_password_encrypted else None
        key = decrypt(server.ssh_key_encrypted) if server.ssh_key_encrypted else None
        return password, key

    async def create(
        self, data: ServerCreate, created_by: uuid.UUID | None = None, validate_ssh: bool = True
    ) -> Server:
        server = Server(
            name=data.name,
            host=data.host,
            port=data.port,
            ssh_user=data.ssh_user,
            server_type=data.server_type,
            environment=data.environment,
            monitoring_interval=data.monitoring_interval,
            created_by=created_by,
        )
        self._encrypt_credentials(server, data)

        if validate_ssh:
            ok = self._ssh.test_connection(
                host=data.host,
                port=data.port,
                user=data.ssh_user,
                password=data.ssh_password,
                key=data.ssh_key,
            )
            if not ok:
                raise ExternalServiceError("SSH", f"Cannot connect to {data.host}:{data.port}")

        return await self._servers.create(server)

    async def get(self, server_id: uuid.UUID) -> Server:
        server = await self._servers.get_by_id(server_id)
        if not server:
            raise NotFoundError("Server", server_id)
        return server

    async def update(self, server_id: uuid.UUID, data: ServerUpdate) -> Server:
        server = await self.get(server_id)
        for field in ("name", "host", "port", "ssh_user", "server_type", "environment",
                      "monitoring_interval", "is_active"):
            val = getattr(data, field, None)
            if val is not None:
                setattr(server, field, val)
        self._encrypt_credentials(server, data)
        return await self._servers.update(server)

    async def delete(self, server_id: uuid.UUID) -> None:
        server = await self.get(server_id)
        await self._servers.delete(server)

    async def list(self, is_active: bool | None = None) -> list[Server]:
        return list(await self._servers.list(is_active=is_active))

    async def validate_connectivity(self, server_id: uuid.UUID) -> bool:
        server = await self.get(server_id)
        password, key = self._decrypt_for_ssh(server)
        return self._ssh.test_connection(
            host=server.host,
            port=server.port,
            user=server.ssh_user,
            password=password,
            key=key,
        )
