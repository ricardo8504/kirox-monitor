import uuid
from datetime import UTC, datetime

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, user_repo: UserRepository, audit_repo: AuditLogRepository) -> None:
        self._users = user_repo
        self._audit = audit_repo

    async def login(
        self,
        email: str,
        password: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenResponse:
        user = await self._users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            await self._audit.create(
                AuditLog(
                    action="LOGIN_FAILED",
                    resource="User",
                    resource_id=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                )
            )
            raise UnauthorizedError("Invalid credentials")

        if not user.is_active:
            raise UnauthorizedError("Account is disabled")

        user.last_login = datetime.now(UTC)
        await self._users.update(user)

        await self._audit.create(
            AuditLog(
                user_id=user.id,
                action="LOGIN",
                resource="User",
                resource_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )

        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token, expected_type="refresh")
        user = await self._users.get_by_id(uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        return TokenResponse(
            access_token=create_access_token(str(user.id), user.role.value),
            refresh_token=create_refresh_token(str(user.id)),
        )

    async def get_current_user(self, token: str) -> User:
        payload = decode_token(token, expected_type="access")
        user = await self._users.get_by_id(uuid.UUID(payload["sub"]))
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        return user


class UserService:
    def __init__(self, user_repo: UserRepository) -> None:
        self._users = user_repo

    async def create_user(self, data: UserCreate) -> User:
        if await self._users.get_by_email(data.email):
            raise ConflictError(f"Email {data.email} already registered")
        if await self._users.get_by_username(data.username):
            raise ConflictError(f"Username {data.username} already taken")
        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        return await self._users.create(user)

    async def get_user(self, user_id: uuid.UUID) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def change_password(self, user_id: uuid.UUID, current: str, new: str) -> None:
        user = await self.get_user(user_id)
        if not verify_password(current, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")
        user.hashed_password = hash_password(new)
        await self._users.update(user)

