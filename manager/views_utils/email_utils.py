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
):
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