import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_webhook(url: str, payload: dict, headers: dict | None = None) -> bool:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers or {})
            resp.raise_for_status()
        logger.info("webhook_sent", url=url)
        return True
    except Exception as exc:
        logger.error("webhook_failed", error=str(exc), url=url)
        return False
