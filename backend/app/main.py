import asyncio
import json
import uuid as uuid_lib
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.limiter import limiter
from app.core.logging import get_logger, setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.core.websocket_manager import ws_manager

logger = get_logger(__name__)

_WS_CHANNEL_PATTERN = "ws:metrics:*"
_WS_CHANNEL_PREFIX = "ws:metrics:"


async def _redis_subscriber() -> None:
    backoff = 1
    while True:
        try:
            r = aioredis.from_url(settings.redis_url)
            pubsub = r.pubsub()
            await pubsub.psubscribe(_WS_CHANNEL_PATTERN)
            logger.info("ws_redis_subscriber_started")
            backoff = 1
            async for message in pubsub.listen():
                if message["type"] != "pmessage":
                    continue
                try:
                    raw_channel = message["channel"]
                    channel = raw_channel.decode() if isinstance(raw_channel, bytes) else raw_channel
                    server_id_str = channel.removeprefix(_WS_CHANNEL_PREFIX)
                    data = json.loads(message["data"])
                    await ws_manager.broadcast_to_server(uuid_lib.UUID(server_id_str), data)
                except Exception as exc:
                    logger.warning("ws_redis_forward_error", error=str(exc))
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("ws_redis_subscriber_reconnecting", error=str(exc), backoff_s=backoff)
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, 60)


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[no-untyped-def]
    setup_logging(log_level=settings.log_level, is_development=settings.is_development)
    subscriber_task = asyncio.create_task(_redis_subscriber())
    yield
    subscriber_task.cancel()
    try:
        await subscriber_task
    except asyncio.CancelledError:
        pass


def create_app() -> FastAPI:
    app = FastAPI(
        title="Odoo Monitor",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    from app.api.v1.alerts import router as alerts_router
    from app.api.v1.auth import router as auth_router
    from app.api.v1.health import router as health_router
    from app.api.v1.metrics import router as metrics_router
    from app.api.v1.servers import router as servers_router
    from app.api.v1.users import router as users_router
    from app.api.v1.ws import router as ws_router

    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(servers_router, prefix="/api/v1")
    app.include_router(metrics_router, prefix="/api/v1")
    app.include_router(alerts_router, prefix="/api/v1")
    app.include_router(ws_router)

    return app


app = create_app()
