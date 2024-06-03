import hashlib
from urllib.parse import urlencode

from django import template
from ..models import Account

register = template.Library()

@register.filter
def gravatar_url(email, size=55):
    default = "https://upload.wikimedia.org/wikipedia/commons/5/5f/Gravatar-default-logo.jpg"
    email_encoded = email.lower().encode('utf-8')
    email_hash = hashlib.sha256(email_encoded).hexdigest()
    params = urlencode({'d': default, 's': str(size)})
    return f"https://www.gravatar.com/avatar/{email_hash}?{params}"

@register.filter
def get_avatar(user: Account) -> str:
    if user.avatar:
        return user.avatar.url
    return gravatar_url(user.email)