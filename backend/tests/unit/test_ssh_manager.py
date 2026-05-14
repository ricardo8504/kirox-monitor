from unittest.mock import MagicMock, patch

import paramiko
import pytest

from app.core.exceptions import ExternalServiceError
from app.services.ssh_manager import SSHManager


@pytest.fixture
def manager():
    return SSHManager(timeout=5)


def test_test_connection_success(manager):
    with patch.object(manager, "_connect") as mock_connect:
        mock_client = MagicMock()
        mock_connect.return_value = mock_client
        result = manager.test_connection("10.0.0.1", 22, "ubuntu", password="secret")
        assert result is True
        mock_client.close.assert_called_once()


def test_test_connection_failure(manager):
    with patch.object(manager, "_connect", side_effect=ExternalServiceError("SSH", "refused")):
        result = manager.test_connection("10.0.0.1", 22, "ubuntu", password="wrong")
        assert result is False


def test_execute_command_success(manager):
    mock_client = MagicMock()
    mock_stdout = MagicMock()
    mock_stdout.read.return_value = b"output"
    mock_stdout.channel.recv_exit_status.return_value = 0
    mock_stderr = MagicMock()
    mock_stderr.read.return_value = b""
    mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)

    with patch.object(manager, "_connect", return_value=mock_client):
        result = manager.execute_command("10.0.0.1", 22, "ubuntu", "ls", password="p")

    assert result.stdout == "output"
    assert result.exit_code == 0
    mock_client.close.assert_called_once()


def test_connect_auth_failure(manager):
    with patch("paramiko.SSHClient") as MockSSH:
        mock_client = MagicMock()
        MockSSH.return_value = mock_client
        mock_client.connect.side_effect = paramiko.AuthenticationException()

        with pytest.raises(ExternalServiceError, match="Authentication failed"):
            manager._connect("10.0.0.1", 22, "ubuntu", password="wrong")


def test_connect_generic_failure(manager):
    with patch("paramiko.SSHClient") as MockSSH:
        mock_client = MagicMock()
        MockSSH.return_value = mock_client
        mock_client.connect.side_effect = OSError("Connection refused")

        with pytest.raises(ExternalServiceError, match="Cannot connect"):
            manager._connect("10.0.0.1", 22, "ubuntu", password="p")
