from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import asyncio
from app.schemas.interview.email_schema import EmailRequest
from app.core.config import settings
from app.core.logger import get_custom_logger

logger = get_custom_logger(app_name="email_service")

def send_email(request: EmailRequest) -> None:
    recipients = request.to_emails + request.cc_emails + request.bcc_emails
    logger.info(f"Sending email to: {recipients}, subject: {request.subject}")
    logger.info(f"SMTP: {settings.SMTP_HOST}:{settings.SMTP_PORT}, user: {settings.SMTP_USER}, from: {request.from_email}")
    
    msg = MIMEMultipart('alternative')
    msg["Subject"] = request.subject
    msg["From"] = request.from_email
    msg["To"] = ", ".join(request.to_emails)
    
    if request.cc_emails:
        msg["Cc"] = ", ".join(request.cc_emails)
    if request.bcc_emails:
        msg["Bcc"] = ", ".join(request.bcc_emails)
    
    msg.attach(MIMEText(request.body, 'html'))
    
    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as smtp:
        smtp.set_debuglevel(1)
        smtp.starttls()
        smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        result = smtp.sendmail(request.from_email, recipients, msg.as_string())
        logger.info(f"SMTP sendmail result: {result}")

async def send_email_async(request: EmailRequest) -> bool:
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, send_email, request)
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False
