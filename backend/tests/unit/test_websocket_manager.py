import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from starlette.websockets import WebSocketState

from app.core.websocket_manager import ConnectionManager


def make_ws(connected: bool = True) -> MagicMock:
    ws = AsyncMock()
    ws.client_state = WebSocketState.CONNECTED if connected else WebSocketState.DISCONNECTED
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.fixture
def manager():
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect_registers_websocket(manager):
    ws = make_ws()
    user_id = uuid.uuid4()
    server_id = uuid.uuid4()

    await manager.connect(ws, server_id, user_id)

    assert ws in manager._server_connections[str(server_id)]
    assert ws in manager._user_connections[str(user_id)]
    ws.accept.assert_called_once()


@pytest.mark.asyncio
async def test_disconnect_removes_websocket(manager):
    ws = make_ws()
    user_id = uuid.uuid4()
    server_id = uuid.uuid4()

    await manager.connect(ws, server_id, user_id)
    manager.disconnect(ws, server_id, user_id)

    assert ws not in manager._server_connections[str(server_id)]
    assert ws not in manager._user_connections[str(user_id)]


@pytest.mark.asyncio
async def test_broadcast_to_server_sends_to_connected(manager):
    ws = make_ws(connected=True)
    user_id = uuid.uuid4()
    server_id = uuid.uuid4()

    await manager.connect(ws, server_id, user_id)
    await manager.broadcast_to_server(server_id, {"cpu": 80.0})

    ws.send_json.assert_called_once_with({"cpu": 80.0})


@pytest.mark.asyncio
async def test_broadcast_to_server_removes_dead_connections(manager):
    ws = make_ws(connected=False)
    user_id = uuid.uuid4()
    server_id = uuid.uuid4()

    await manager.connect(ws, server_id, user_id)
    # Manually set disconnected state
    ws.client_state = WebSocketState.DISCONNECTED
    await manager.broadcast_to_server(server_id, {"cpu": 80.0})

    assert ws not in manager._server_connections[str(server_id)]


@pytest.mark.asyncio
async def test_broadcast_to_user(manager):
    ws = make_ws()
    user_id = uuid.uuid4()

    await manager.connect(ws, None, user_id)
    await manager.broadcast_to_user(user_id, {"alert": "high cpu"})

    ws.send_json.assert_called_once_with({"alert": "high cpu"})


@pytest.mark.asyncio
async def test_connect_without_server_id(manager):
    ws = make_ws()
    user_id = uuid.uuid4()

    await manager.connect(ws, None, user_id)

    assert ws in manager._user_connections[str(user_id)]
    # No server connections registered
    assert all(ws not in conns for conns in manager._server_connections.values())
