import json
import uuid

from app.core.encryption import decrypt
from app.core.logging import get_logger
from app.models.alert import AlertEvent, ChannelType
from app.repositories.alert_repository import NotificationChannelRepository
from app.services.notifications.email_notifier import send_email
from app.services.notifications.telegram_notifier import send_telegram
from app.services.notifications.webhook_notifier import send_webhook

logger = get_logger(__name__)


class NotificationDispatcher:
    def __init__(self, channel_repo: NotificationChannelRepository) -> None:
        self._channels = channel_repo

    async def dispatch(self, event: AlertEvent, user_id: uuid.UUID) -> None:
        channels = await self._channels.list_by_user(user_id)
        for channel in channels:
            if not channel.enabled:
                continue
            try:
                config: dict = json.loads(decrypt(channel.config_encrypted))
            except Exception:
                logger.warning("channel_config_decrypt_failed", channel_id=str(channel.id))
                continue

            if channel.channel_type == ChannelType.EMAIL:
                await send_email(
                    to=config.get("to", ""),
                    subject=f"[{event.severity}] Alert: {event.message[:50]}",
                    body_html=f"<p>{event.message}</p><p>Value: {event.metric_value}</p>",
                )
            elif channel.channel_type == ChannelType.TELEGRAM:
                await send_telegram(
                    bot_token=config.get("bot_token", ""),
                    chat_id=config.get("chat_id", ""),
                    message=f"[{event.severity}] {event.message}",
                )
            elif channel.channel_type == ChannelType.WEBHOOK:
                await send_webhook(
                    url=config.get("url", ""),
                    payload={
                        "severity": event.severity,
                        "message": event.message,
                        "value": event.metric_value,
                    },
                    headers=config.get("headers"),
                )
