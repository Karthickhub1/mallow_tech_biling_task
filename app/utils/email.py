import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_invoice_email(to_email: str, invoice_html: str) -> bool:
    """Send invoice email to the customer. Returns True if successful."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured. Skipping email send to %s", to_email)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Invoice from {settings.APP_NAME}"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.attach(MIMEText(invoice_html, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
        logger.info("Invoice email sent to %s", to_email)
        return True
    except Exception:
        logger.exception("Failed to send invoice email to %s", to_email)
        return False
