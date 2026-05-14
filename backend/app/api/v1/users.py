import uuid

from fastapi import APIRouter, Depends

from app.core.deps import get_user_service, require_roles
from app.models.user import UserRole
from app.schemas.user import UserCreate, UserListResponse, UserResponse
from app.services.auth_service import UserService

router = APIRouter(prefix="/users", tags=["users"])

_admin = require_roles(UserRole.ADMIN)


@router.get("", response_model=UserListResponse, dependencies=[Depends(_admin)])
async def list_users(
    limit: int = 100,
    offset: int = 0,
    svc: UserService = Depends(get_user_service),
) -> UserListResponse:
    items = await svc._users.list(limit=limit, offset=offset)
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in items],
        total=len(items),
    )


@router.post("", response_model=UserResponse, dependencies=[Depends(_admin)])
async def create_user(
    body: UserCreate,
    svc: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await svc.create_user(body)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse, dependencies=[Depends(_admin)])
async def get_user(
    user_id: uuid.UUID,
    svc: UserService = Depends(get_user_service),
) -> UserResponse:
    user = await svc.get_user(user_id)
    return UserResponse.model_validate(user)
