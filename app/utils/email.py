import logging
import os

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Template

from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_conf() -> ConnectionConfig:
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=settings.USE_CREDENTIALS,
        VALIDATE_CERTS=settings.VALIDATE_CERTS,
    )


async def send_email(
    subject: str,
    recipients: list[str],
    raw_template: str,
    context: dict | None = None,
    attachments: list[str] | None = None,
    render_jinja: bool = True,
) -> dict:
    """Send an HTML email. Returns {'is_success': bool, 'message': str}."""
    logger.info("---Start send_email---")
    context = context or {}

    if not settings.MAIL_USERNAME or not settings.MAIL_PASSWORD:
        logger.warning("Mail credentials not configured. Skipping send to %s", recipients)
        logger.info("---End---")
        return {"is_success": False, "message": "Mail credentials not configured"}

    if render_jinja:
        logger.info("Rendering body using Jinja2")
        try:
            body = Template(raw_template).render(**context)
        except Exception as e:
            logger.exception("Template rendering error")
            logger.info("---End---")
            return {"is_success": False, "message": f"Template rendering error: {e}"}
    else:
        logger.info("Replacing placeholders in template with context values")
        body = raw_template
        for key, value in context.items():
            body = body.replace(f"{{{{ {key} }}}}", str(value))

    attachment_list = []
    if attachments:
        for file_path in attachments:
            if os.path.exists(file_path):
                attachment_list.append(file_path)
            else:
                logger.warning("Attachment not found, skipping: %s", file_path)

    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html,
        attachments=attachment_list,
    )

    fm = FastMail(_build_conf())
    try:
        await fm.send_message(message)
        logger.info("Email sent successfully to %s", recipients)
        logger.info("---End---")
        return {"is_success": True, "message": f"Email sent successfully to {recipients}"}
    except Exception as e:
        logger.exception("Error sending email to %s", recipients)
        logger.info("---End---")
        return {"is_success": False, "message": f"Error sending email: {e}"}


INVOICE_EMAIL_TEMPLATE = """\
<!DOCTYPE html>
<html>
<head><style>
    body { font-family: Arial, sans-serif; }
    table { border-collapse: collapse; width: 100%; margin: 10px 0; }
    th, td { border: 1px solid #ccc; padding: 6px; text-align: center; }
    th { background: #f0f0f0; }
</style></head>
<body>
<h2>Invoice - {{ app_name }}</h2>
<p><strong>Customer Email:</strong> {{ invoice.customer_email }}</p>
<p><strong>Date:</strong> {{ invoice.created_at.strftime('%Y-%m-%d %H:%M') }}</p>

<table>
    <tr>
        <th>Product ID</th><th>Unit Price</th><th>Qty</th>
        <th>Purchase Price</th><th>Tax %</th><th>Tax Amount</th><th>Total</th>
    </tr>
    {% for item in invoice.items %}
    <tr>
        <td>{{ item.product_id }}</td>
        <td>{{ "%.2f"|format(item.unit_price) }}</td>
        <td>{{ item.quantity }}</td>
        <td>{{ "%.2f"|format(item.purchase_price) }}</td>
        <td>{{ "%.2f"|format(item.tax_percentage) }}%</td>
        <td>{{ "%.2f"|format(item.tax_amount) }}</td>
        <td>{{ "%.2f"|format(item.total_price) }}</td>
    </tr>
    {% endfor %}
</table>

<p><strong>Total without tax:</strong> {{ "%.2f"|format(invoice.total_without_tax) }}</p>
<p><strong>Total tax:</strong> {{ "%.2f"|format(invoice.total_tax) }}</p>
<p><strong>Net price:</strong> {{ "%.2f"|format(invoice.net_price) }}</p>
<p><strong>Rounded net price:</strong> {{ "%.2f"|format(invoice.rounded_net_price) }}</p>
<p><strong>Cash paid:</strong> {{ "%.2f"|format(invoice.cash_paid) }}</p>
<p><strong>Balance:</strong> {{ "%.2f"|format(invoice.balance) }}</p>

{% if balance_denominations %}
<h3>Balance Denomination:</h3>
<ul>
    {% for value, count in balance_denominations.items() %}
    <li>{{ value }}: {{ count }}</li>
    {% endfor %}
</ul>
{% endif %}

<p>Thank you for your purchase!</p>
</body>
</html>
"""


async def send_invoice_email(to_email: str, invoice, balance_denominations: dict) -> dict:
    """Render and send the invoice email to the customer."""
    return await send_email(
        subject=f"Invoice from {settings.APP_NAME}",
        recipients=[to_email],
        raw_template=INVOICE_EMAIL_TEMPLATE,
        context={
            "app_name": settings.APP_NAME,
            "invoice": invoice,
            "balance_denominations": balance_denominations,
        },
    )
