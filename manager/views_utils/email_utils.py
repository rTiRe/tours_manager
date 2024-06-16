"""Module with functions for work with email."""

from os import getenv

from django.core import mail
from django.utils import html
from dotenv import load_dotenv

load_dotenv()


def send_email(
    mail_subject: str,
    message: str,
    recipient_list: list | tuple,
    render_message_to_html: bool = True,
) -> None:
    """Send email to the specified address.

    Args:
        mail_subject: str - subject of email.
        message: str - email message.
        recipient_list: list | tuple - list of recipients.
        render_message_to_html: bool, optional - If needs render message to html. Defaults to True.
    """
    if render_message_to_html:
        plain_message = html.strip_tags(message)
    else:
        plain_message = message
    mail.send_mail(
        mail_subject,
        plain_message,
        getenv('SMTP_FROM_EMAIL'),
        recipient_list,
        html_message=message,
    )
