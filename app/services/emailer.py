# app/services/emailer.py
import aiosmtplib
from email.message import EmailMessage
from ..config import settings


async def send_qr_email(
    *,
    to_email: str,
    subject: str,
    body_text: str,
    attachment_bytes: bytes,
    attachment_filename: str,
) -> None:
    # Ensure SMTP settings are properly configured. The default value in
    # the example `.env` uses a placeholder host (`smtp.tu-proveedor.com`).
    # Treat this placeholder as missing configuration so the application
    # fails fast with a clear error instead of trying to resolve a
    # non-existent domain and raising a connection error.
    if (
        not settings.SMTP_HOST
        or settings.SMTP_HOST == "smtp.tu-proveedor.com"
        or not settings.MAIL_FROM
    ):
        raise RuntimeError("SMTP settings are not configured")

    msg = EmailMessage()
    msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body_text)

    msg.add_attachment(
        attachment_bytes,
        maintype="image",
        subtype="png",
        filename=attachment_filename,
    )

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USERNAME,
        password=settings.SMTP_PASSWORD,
        start_tls=settings.SMTP_TLS,
    )


