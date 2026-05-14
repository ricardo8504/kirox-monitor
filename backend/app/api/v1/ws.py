import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.exceptions import UnauthorizedError
from app.core.logging import get_logger
from app.core.security import decode_token
from app.core.websocket_manager import ws_manager

router = APIRouter(tags=["websockets"])

logger = get_logger(__name__)


async def _auth_token(token: str | None) -> dict:
    if not token:
        raise UnauthorizedError("Missing token")
    return decode_token(token, expected_type="access")


@router.websocket("/ws/metrics/{server_id}")
async def ws_metrics(
    websocket: WebSocket,
    server_id: uuid.UUID,
    token: str | None = None,
) -> None:
    try:
        payload = await _auth_token(token)
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, server_id, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, server_id, user_id)


@router.websocket("/ws/alerts")
async def ws_alerts(
    websocket: WebSocket,
    token: str | None = None,
) -> None:
    try:
        payload = await _auth_token(token)
        user_id = uuid.UUID(payload["sub"])
    except Exception:
        await websocket.close(code=4001)
        return

    await ws_manager.connect(websocket, None, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, None, user_id)
