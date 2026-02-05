from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.core.config import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs,
)


async def send_email(subject: str, recipients: list[EmailStr], body: str):
    """Send an email using the configured SMTP server."""

    message = MessageSchema(
        subject=subject, recipients=recipients, body=body, subtype=MessageType.html
    )

    fm = FastMail(conf)
    await fm.send_message(message)


async def send_otp_email(email: EmailStr, otp: str):
    """Send OTP verification email."""
    subject = "Your AARLP Verification Code"
    # A simple HTML template
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #333333; text-align: center;">Verification Code</h2>
                <p style="color: #666666; font-size: 16px;">Hello,</p>
                <p style="color: #666666; font-size: 16px;">Your verification code for AARLP is:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #4F46E5; background-color: #EEF2FF; padding: 10px 20px; border-radius: 8px;">{otp}</span>
                </div>
                <p style="color: #666666; font-size: 14px;">This code will expire in 10 minutes.</p>
                <p style="color: #666666; font-size: 14px;">If you didn't request this, please ignore this email.</p>
                <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 20px 0;">
                <p style="color: #999999; font-size: 12px; text-align: center;">© 2026 AARLP Platform</p>
            </div>
        </body>
    </html>
    """
    await send_email(subject, [email], html)


async def send_password_reset_email(email: EmailStr, otp: str):
    """Send password reset OTP email."""
    subject = "Reset Your AARLP Password"
    # A simple HTML template
    html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="color: #333333; text-align: center;">Password Reset Request</h2>
                <p style="color: #666666; font-size: 16px;">Hello,</p>
                <p style="color: #666666; font-size: 16px;">We received a request to reset your password for AARLP. Your verification code is:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #DC2626; background-color: #FEF2F2; padding: 10px 20px; border-radius: 8px;">{otp}</span>
                </div>
                <p style="color: #666666; font-size: 14px;">This code will expire in 10 minutes.</p>
                <p style="color: #666666; font-size: 14px;">If you didn't request a password reset, you can safely ignore this email.</p>
                <hr style="border: 0; border-top: 1px solid #eeeeee; margin: 20px 0;">
                <p style="color: #999999; font-size: 12px; text-align: center;">© 2026 AARLP Platform</p>
            </div>
        </body>
    </html>
    """
    await send_email(subject, [email], html)
