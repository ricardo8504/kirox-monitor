from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_email(to: str, subject: str, body_html: str) -> bool:
    if not settings.smtp_host:
        logger.warning("smtp_not_configured")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg.attach(MIMEText(body_html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            use_tls=settings.smtp_tls,
        )
        logger.info("email_sent", to=to, subject=subject)
        return True
    except Exception as exc:
        logger.error("email_failed", error=str(exc), to=to)
        return False


def alert_email_body(
    server_name: str, metric: str, value: float, threshold: float, severity: str
) -> str:
    _colors = {"INFO": "#3b82f6", "WARNING": "#f59e0b", "CRITICAL": "#ef4444"}
    color = _colors.get(severity, "#6b7280")
    return f"""
    <html><body>
    <h2 style="color:{color}">[{severity}] Odoo Monitor Alert</h2>
    <p><strong>Server:</strong> {server_name}</p>
    <p><strong>Metric:</strong> {metric}</p>
    <p><strong>Value:</strong> {value}</p>
    <p><strong>Threshold:</strong> {threshold}</p>
    </body></html>
    """
