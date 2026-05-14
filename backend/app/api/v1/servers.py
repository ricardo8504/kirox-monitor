import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.repositories.server_repository import ServerRepository
from app.schemas.server import ServerCreate, ServerListResponse, ServerResponse, ServerUpdate
from app.services.server_service import ServerService
from app.services.ssh_manager import ssh_manager

router = APIRouter(prefix="/servers", tags=["servers"])

_any_role = require_roles(UserRole.ADMIN, UserRole.OPERATOR, UserRole.READONLY)
_write_role = require_roles(UserRole.ADMIN, UserRole.OPERATOR)
_admin = require_roles(UserRole.ADMIN)


def get_server_service(db: AsyncSession = Depends(get_db)) -> ServerService:
    return ServerService(ServerRepository(db), manager=ssh_manager)


@router.get("", response_model=ServerListResponse, dependencies=[Depends(_any_role)])
async def list_servers(svc: ServerService = Depends(get_server_service)) -> ServerListResponse:
    items = await svc.list()
    return ServerListResponse(
        items=[ServerResponse.model_validate(s) for s in items],
        total=len(items),
    )


@router.post("", response_model=ServerResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(_write_role)])
async def create_server(
    body: ServerCreate,
    user: User = Depends(get_current_user),
    svc: ServerService = Depends(get_server_service),
) -> ServerResponse:
    server = await svc.create(body, created_by=user.id, validate_ssh=False)
    return ServerResponse.model_validate(server)


@router.get("/{server_id}", response_model=ServerResponse, dependencies=[Depends(_any_role)])
async def get_server(
    server_id: uuid.UUID,
    svc: ServerService = Depends(get_server_service),
) -> ServerResponse:
    server = await svc.get(server_id)
    return ServerResponse.model_validate(server)


@router.put("/{server_id}", response_model=ServerResponse, dependencies=[Depends(_write_role)])
async def update_server(
    server_id: uuid.UUID,
    body: ServerUpdate,
    svc: ServerService = Depends(get_server_service),
) -> ServerResponse:
    server = await svc.update(server_id, body)
    return ServerResponse.model_validate(server)


@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(_admin)])
async def delete_server(
    server_id: uuid.UUID,
    svc: ServerService = Depends(get_server_service),
) -> None:
    await svc.delete(server_id)


@router.post("/{server_id}/test-connection", dependencies=[Depends(_write_role)])
async def test_connection(
    server_id: uuid.UUID,
    svc: ServerService = Depends(get_server_service),
) -> dict:
    ok = await svc.validate_connectivity(server_id)
    return {"server_id": str(server_id), "connected": ok}
