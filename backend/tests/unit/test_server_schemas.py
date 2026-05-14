import pytest
from pydantic import ValidationError

from app.schemas.server import ServerCreate, ServerUpdate


def test_server_create_valid_password():
    s = ServerCreate(name="prod1", host="10.0.0.1", ssh_user="ubuntu", ssh_password="secret")
    assert s.port == 22
    assert s.monitoring_interval == 60


def test_server_create_valid_key():
    s = ServerCreate(name="prod1", host="10.0.0.1", ssh_user="ubuntu", ssh_key="-----BEGIN...")
    assert s.ssh_key == "-----BEGIN..."


def test_server_create_no_auth_raises():
    with pytest.raises(ValidationError, match="ssh_password or ssh_key"):
        ServerCreate(name="s", host="h", ssh_user="u")


def test_server_create_invalid_port_zero():
    with pytest.raises(ValidationError, match="Port"):
        ServerCreate(name="s", host="h", ssh_user="u", ssh_password="p", port=0)


def test_server_create_invalid_port_too_high():
    with pytest.raises(ValidationError):
        ServerCreate(name="s", host="h", ssh_user="u", ssh_password="p", port=99999)


def test_server_create_invalid_interval():
    with pytest.raises(ValidationError, match="10 seconds"):
        ServerCreate(name="s", host="h", ssh_user="u", ssh_password="p", monitoring_interval=5)


def test_server_update_partial():
    u = ServerUpdate(is_active=False)
    assert u.name is None
    assert u.is_active is False
