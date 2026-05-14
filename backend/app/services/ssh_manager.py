import io
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Generator

import paramiko

from app.core.config import settings
from app.core.exceptions import ExternalServiceError


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int


class SSHManager:
    def __init__(self, timeout: int | None = None) -> None:
        self._timeout = timeout or settings.ssh_timeout

    def _connect(
        self,
        host: str,
        port: int,
        user: str,
        password: str | None = None,
        key: str | None = None,
    ) -> paramiko.SSHClient:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # noqa: S507
        kwargs: dict = {
            "hostname": host,
            "port": port,
            "username": user,
            "timeout": self._timeout,
            "allow_agent": False,
            "look_for_keys": False,
        }
        if key:
            pkey = paramiko.RSAKey.from_private_key(io.StringIO(key))
            kwargs["pkey"] = pkey
        else:
            kwargs["password"] = password
        try:
            client.connect(**kwargs)
        except paramiko.AuthenticationException as exc:
            raise ExternalServiceError("SSH", f"Authentication failed for {user}@{host}") from exc
        except Exception as exc:
            raise ExternalServiceError("SSH", f"Cannot connect to {host}:{port} — {exc}") from exc
        return client

    @contextmanager
    def get_connection(
        self,
        host: str,
        port: int,
        user: str,
        password: str | None = None,
        key: str | None = None,
    ) -> Generator[paramiko.SSHClient, None, None]:
        client = self._connect(host, port, user, password=password, key=key)
        try:
            yield client
        finally:
            client.close()

    def execute_command_on(self, client: paramiko.SSHClient, command: str) -> "CommandResult":
        try:
            _, stdout, stderr = client.exec_command(command, timeout=self._timeout)
            exit_code = stdout.channel.recv_exit_status()
            return CommandResult(
                stdout=stdout.read().decode(errors="replace"),
                stderr=stderr.read().decode(errors="replace"),
                exit_code=exit_code,
            )
        except Exception as exc:
            raise ExternalServiceError("SSH", str(exc)) from exc

    def test_connection(
        self,
        host: str,
        port: int,
        user: str,
        password: str | None = None,
        key: str | None = None,
    ) -> bool:
        try:
            client = self._connect(host, port, user, password=password, key=key)
            client.close()
            return True
        except ExternalServiceError:
            return False

    def execute_command(
        self,
        host: str,
        port: int,
        user: str,
        command: str,
        password: str | None = None,
        key: str | None = None,
    ) -> CommandResult:
        client = self._connect(host, port, user, password=password, key=key)
        try:
            _, stdout, stderr = client.exec_command(command, timeout=self._timeout)
            exit_code = stdout.channel.recv_exit_status()
            return CommandResult(
                stdout=stdout.read().decode(errors="replace"),
                stderr=stderr.read().decode(errors="replace"),
                exit_code=exit_code,
            )
        finally:
            client.close()


ssh_manager = SSHManager()
