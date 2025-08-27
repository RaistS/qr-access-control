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
    if not settings.SMTP_HOST or not settings.MAIL_FROM:
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


