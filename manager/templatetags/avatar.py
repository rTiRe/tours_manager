import hashlib
from urllib.parse import urlencode

from django import template
from ..models import Account, Tour

from django.templatetags.static import static

register = template.Library()

DEFAULT = 'https://i.imgur.com/9D119KO.png'

@register.filter
def gravatar_url(email, size=55):
    default = DEFAULT
    email_encoded = email.lower().encode('utf-8')
    email_hash = hashlib.sha256(email_encoded).hexdigest()
    params = urlencode({'d': default, 's': str(size)})
    return f'https://www.gravatar.com/avatar/{email_hash}?{params}'

@register.filter
def get_avatar(user: Account) -> str:
    if user.avatar:
        return user.avatar.url
    return gravatar_url(user.email)

@register.filter
def get_tour_cover(tour: Tour) -> str:
    if tour.avatar:
        return tour.avatar.url
    return DEFAULT