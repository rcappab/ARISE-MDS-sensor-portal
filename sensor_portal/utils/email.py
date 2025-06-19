import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from user_management.models import User

logger = logging.getLogger(__name__)


def send_email_to_users(users: list[User], subject: str, body: str):
    for user in users:
        send_email_to_user(user, subject, body)


def send_email_to_user(user: User, subject: str, body: str):
    try:
        user.deviceuser
        return
    except User.deviceuser.RelatedObjectDoesNotExist:
        pass

    new_body = render_to_string(
        "email_body.html", {"user": user, "body": body})

    send_email(user.email, subject, new_body)


def send_email(to_email, subject, body):
    try:
        settings.EMAIL_HOST_USER
    except AttributeError:
        logger.info("No email sender configured")
        return

    if not to_email:
        raise ValueError(
            "The 'to_email' address must be provided and cannot be empty.")
    elif not isinstance(to_email, list):
        to_email = [to_email]

    try:
        html_message = render_to_string(
            "email.html", {"body": body})
        message = EmailMessage(subject=subject,
                               body=html_message,
                               from_email=settings.EMAIL_HOST_USER,
                               to=to_email)
        message.content_subtype = 'html'
        result = message.send()
        logger.info(
            f"Sending email to {', '.join(to_email)} with subject: {subject} - Status {result}")
    except Exception as e:
        logger.error(
            f"Sending email to {', '.join(to_email)} with subject: {subject} - Status 0")
        logger.error(e)
