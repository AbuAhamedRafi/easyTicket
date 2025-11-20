"""
Celery tasks for Common app
Handles asynchronous operations like email sending
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_task(self, subject, message, recipient_list, html_message=None):
    """
    Send email asynchronously using Celery

    Args:
        subject (str): Email subject
        message (str): Plain text message
        recipient_list (list): List of recipient email addresses
        html_message (str, optional): HTML version of the message

    Returns:
        dict: Status of email sending operation
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent successfully to {recipient_list}")
        return {
            "status": "success",
            "message": f"Email sent to {len(recipient_list)} recipient(s)",
        }
    except Exception as exc:
        logger.error(f"Email sending failed: {str(exc)}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task
def send_verification_email_task(email, verification_token):
    """
    Send email verification link asynchronously

    Args:
        email (str): User's email address
        verification_token (str): Verification token UUID
    """
    from Common.email_utils import send_verification_email

    try:
        send_verification_email(email, verification_token)
        logger.info(f"Verification email sent to {email}")
        return {"status": "success", "email": email}
    except Exception as exc:
        logger.error(f"Failed to send verification email to {email}: {str(exc)}")
        raise


@shared_task
def send_password_reset_email_task(email, reset_token):
    """
    Send password reset email asynchronously

    Args:
        email (str): User's email address
        reset_token (str): Password reset token UUID
    """
    from Common.email_utils import send_password_reset_email

    try:
        send_password_reset_email(email, reset_token)
        logger.info(f"Password reset email sent to {email}")
        return {"status": "success", "email": email}
    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {str(exc)}")
        raise


@shared_task
def send_welcome_email_task(email, first_name):
    """
    Send welcome email to new users

    Args:
        email (str): User's email address
        first_name (str): User's first name
    """
    from Common.email_utils import send_welcome_email

    try:
        send_welcome_email(email, first_name)
        logger.info(f"Welcome email sent to {email}")
        return {"status": "success", "email": email}
    except Exception as exc:
        logger.error(f"Failed to send welcome email to {email}: {str(exc)}")
        raise
