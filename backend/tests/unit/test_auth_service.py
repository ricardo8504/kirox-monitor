import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService, UserService


def make_user(active: bool = True) -> User:
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = "test@example.com"
    user.username = "testuser"
    user.hashed_password = hash_password("password123")
    user.role = UserRole.READONLY
    user.is_active = active
    return user


@pytest.fixture
def user_repo():
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def audit_repo():
    return AsyncMock(spec=AuditLogRepository)


@pytest.fixture
def auth_service(user_repo, audit_repo):
    return AuthService(user_repo, audit_repo)


@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo)


# --- AuthService ---

@pytest.mark.asyncio
async def test_login_success(auth_service, user_repo):
    user = make_user()
    user_repo.get_by_email.return_value = user
    user_repo.update.return_value = user
    audit_repo_mock = auth_service._audit
    audit_repo_mock.create.return_value = None

    tokens = await auth_service.login("test@example.com", "password123")
    assert tokens.access_token
    assert tokens.refresh_token
    assert tokens.token_type == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(auth_service, user_repo):
    user = make_user()
    user_repo.get_by_email.return_value = user
    auth_service._audit.create.return_value = None

    with pytest.raises(UnauthorizedError, match="Invalid credentials"):
        await auth_service.login("test@example.com", "wrongpass")


@pytest.mark.asyncio
async def test_login_user_not_found(auth_service, user_repo):
    user_repo.get_by_email.return_value = None
    auth_service._audit.create.return_value = None

    with pytest.raises(UnauthorizedError):
        await auth_service.login("noone@example.com", "password123")


@pytest.mark.asyncio
async def test_login_inactive_user(auth_service, user_repo):
    user = make_user(active=False)
    user_repo.get_by_email.return_value = user

    with pytest.raises(UnauthorizedError, match="disabled"):
        await auth_service.login("test@example.com", "password123")


@pytest.mark.asyncio
async def test_refresh_token(auth_service, user_repo):
    from app.core.security import create_refresh_token
    user = make_user()
    user_repo.get_by_id.return_value = user
    token = create_refresh_token(str(user.id))

    tokens = await auth_service.refresh(token)
    assert tokens.access_token


@pytest.mark.asyncio
async def test_get_current_user(auth_service, user_repo):
    from app.core.security import create_access_token
    user = make_user()
    user_repo.get_by_id.return_value = user
    token = create_access_token(str(user.id), "READONLY")

    result = await auth_service.get_current_user(token)
    assert result.id == user.id


# --- UserService ---

@pytest.mark.asyncio
async def test_create_user_success(user_service, user_repo):
    user_repo.get_by_email.return_value = None
    user_repo.get_by_username.return_value = None
    created = make_user()
    user_repo.create.return_value = created

    data = UserCreate(email="new@example.com", username="newuser", password="securepass")
    result = await user_service.create_user(data)
    assert result is created


@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service, user_repo):
    user_repo.get_by_email.return_value = make_user()

    with pytest.raises(ConflictError, match="already registered"):
        await user_service.create_user(
            UserCreate(email="dup@example.com", username="other", password="securepass")
        )


@pytest.mark.asyncio
async def test_change_password_wrong_current(user_service, user_repo):
    user = make_user()
    user_repo.get_by_id.return_value = user

    with pytest.raises(UnauthorizedError, match="incorrect"):
        await user_service.change_password(user.id, "wrongcurrent", "newpass123")
