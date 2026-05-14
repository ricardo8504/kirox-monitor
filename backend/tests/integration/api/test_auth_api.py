import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.deps import get_auth_service, get_current_user
from app.core.exceptions import UnauthorizedError
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User, UserRole
from app.schemas.auth import TokenResponse


def make_user(role: UserRole = UserRole.ADMIN) -> MagicMock:
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "admin@example.com"
    user.username = "admin"
    user.hashed_password = hash_password("password123")
    user.role = role
    user.is_active = True
    user.last_login = None
    user.created_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    return user


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_login_success(client):
    user = make_user()
    mock_auth = AsyncMock()
    mock_auth.login.return_value = TokenResponse(
        access_token="access_tok", refresh_token="refresh_tok"
    )

    app.dependency_overrides[get_auth_service] = lambda: mock_auth
    r = client.post("/api/v1/auth/login", json={"email": "admin@example.com", "password": "password123"})
    app.dependency_overrides.clear()

    assert r.status_code == 200
    assert r.json()["access_token"] == "access_tok"


def test_login_invalid_credentials(client):
    mock_auth = AsyncMock()
    mock_auth.login.side_effect = UnauthorizedError("Invalid credentials")

    app.dependency_overrides[get_auth_service] = lambda: mock_auth
    r = client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "wrong"})
    app.dependency_overrides.clear()

    assert r.status_code == 401
    assert r.json()["error"]["code"] == "UNAUTHORIZED"


def test_login_invalid_email_format(client):
    r = client.post("/api/v1/auth/login", json={"email": "not-email", "password": "pass"})
    assert r.status_code == 422


def test_me_no_token(client):
    r = client.get("/api/v1/auth/me")
    assert r.status_code == 401


def test_me_with_valid_token(client):
    user = make_user()

    async def override():
        return user

    app.dependency_overrides[get_current_user] = override
    r = client.get("/api/v1/auth/me")
    app.dependency_overrides.clear()

    assert r.status_code == 200


def test_refresh_token(client):
    mock_auth = AsyncMock()
    mock_auth.refresh.return_value = TokenResponse(
        access_token="new_access", refresh_token="new_refresh"
    )
    app.dependency_overrides[get_auth_service] = lambda: mock_auth
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": "some_token"})
    app.dependency_overrides.clear()

    assert r.status_code == 200
    assert r.json()["access_token"] == "new_access"
