from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app


async def mock_db():
    session = AsyncMock()
    session.execute = AsyncMock()
    yield session


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = mock_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_health_returns_200(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200


def test_health_response_structure(client):
    r = client.get("/api/v1/health")
    body = r.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "db" in body
    assert "env" in body
