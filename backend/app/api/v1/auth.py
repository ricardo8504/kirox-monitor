from fastapi import APIRouter, Depends, Request

from app.core.config import settings
from app.core.deps import get_auth_service, get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_login)
async def login(
    request: Request,
    body: LoginRequest,
    auth: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent")
    return await auth.login(body.email, body.password, ip_address=ip, user_agent=ua)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_refresh)
async def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
    auth: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    return await auth.refresh(body.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)) -> User:
    return user
