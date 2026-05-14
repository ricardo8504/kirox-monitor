from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.models.user import User, UserRole
from app.repositories.audit_log_repository import AuditLogRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService, UserService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db), AuditLogRepository(db))


async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(UserRepository(db))


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    if not credentials:
        raise UnauthorizedError("Missing authorization header")
    return await auth.get_current_user(credentials.credentials)


def require_roles(*roles: UserRole):  # type: ignore[no-untyped-def]
    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            from app.core.exceptions import ForbiddenError
            raise ForbiddenError("Insufficient permissions")
        return user
    return _check
