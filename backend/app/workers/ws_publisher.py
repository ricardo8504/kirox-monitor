import json
import uuid

import redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_WS_CHANNEL_PREFIX = "ws:metrics:"


def publish_metrics(server_id: uuid.UUID, data: dict) -> None:
    """Publish metrics snapshot to Redis pub/sub channel."""
    try:
        r = redis.from_url(settings.redis_url)
        channel = f"{_WS_CHANNEL_PREFIX}{server_id}"
        r.publish(channel, json.dumps(data))
        r.close()
    except Exception as exc:
        logger.warning("ws_publish_failed", server_id=str(server_id), error=str(exc))
