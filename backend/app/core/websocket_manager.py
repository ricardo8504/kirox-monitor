import uuid
from collections import defaultdict

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from app.core.logging import get_logger

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        # server_id → set of websockets
        self._server_connections: dict[str, set[WebSocket]] = defaultdict(set)
        # user_id → set of websockets
        self._user_connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(
        self, websocket: WebSocket, server_id: uuid.UUID | None, user_id: uuid.UUID
    ) -> None:
        await websocket.accept()
        uid = str(user_id)
        self._user_connections[uid].add(websocket)
        if server_id:
            self._server_connections[str(server_id)].add(websocket)
        logger.info("ws_connected", user_id=uid, server_id=str(server_id) if server_id else None)

    def disconnect(
        self, websocket: WebSocket, server_id: uuid.UUID | None, user_id: uuid.UUID
    ) -> None:
        uid = str(user_id)
        self._user_connections[uid].discard(websocket)
        if server_id:
            self._server_connections[str(server_id)].discard(websocket)
        logger.info("ws_disconnected", user_id=uid)

    async def broadcast_to_server(self, server_id: uuid.UUID, data: dict) -> None:
        sid = str(server_id)
        dead: set[WebSocket] = set()
        for ws in set(self._server_connections.get(sid, [])):
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(data)
                else:
                    dead.add(ws)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._server_connections[sid].discard(ws)

    async def broadcast_to_user(self, user_id: uuid.UUID, data: dict) -> None:
        uid = str(user_id)
        dead: set[WebSocket] = set()
        for ws in set(self._user_connections.get(uid, [])):
            try:
                if ws.client_state == WebSocketState.CONNECTED:
                    await ws.send_json(data)
                else:
                    dead.add(ws)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self._user_connections[uid].discard(ws)

ws_manager = ConnectionManager()
