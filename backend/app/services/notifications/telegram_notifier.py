import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def send_telegram(bot_token: str, chat_id: str, message: str) -> bool:
    url = _TELEGRAM_API.format(token=bot_token)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                url, json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            )
            resp.raise_for_status()
        logger.info("telegram_sent", chat_id=chat_id)
        return True
    except Exception as exc:
        logger.error("telegram_failed", error=str(exc), chat_id=chat_id)
        return False
