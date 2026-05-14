import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exception_handlers import register_exception_handlers
from app.core.exceptions import (
    ConflictError,
    ExternalServiceError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def make_app(*routes: tuple) -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)
    for path, exc_cls, kwargs in routes:

        @app.get(path)
        async def _endpoint(exc=exc_cls, kw=kwargs):
            raise exc(**kw)

    return TestClient(app, raise_server_exceptions=False)


def test_not_found_returns_404():
    client = make_app(("/", NotFoundError, {"resource": "Server", "resource_id": "123"}))
    r = client.get("/")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_unauthorized_returns_401():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/unauth")
    async def _():
        raise UnauthorizedError()

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/unauth")
    assert r.status_code == 401


def test_forbidden_returns_403():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/forbidden")
    async def _():
        raise ForbiddenError()

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/forbidden")
    assert r.status_code == 403


def test_conflict_returns_409():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/conflict")
    async def _():
        raise ConflictError("already exists")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/conflict")
    assert r.status_code == 409


def test_validation_error_returns_422():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/val")
    async def _():
        raise ValidationError("bad input")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/val")
    assert r.status_code == 422


def test_external_service_error_returns_502():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/ext")
    async def _():
        raise ExternalServiceError("SSH", "connection refused")

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/ext")
    assert r.status_code == 502


def test_error_body_format():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/fmt")
    async def _():
        raise NotFoundError("User")

    client = TestClient(app, raise_server_exceptions=False)
    body = client.get("/fmt").json()
    assert "error" in body
    assert "code" in body["error"]
    assert "message" in body["error"]
