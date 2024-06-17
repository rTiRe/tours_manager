"""Module with methods for find avatars."""

import hashlib
from urllib.parse import urlencode

from django import template

from ..models import Account, Tour

register = template.Library()
DEFAULT = 'https://i.imgur.com/9D119KO.png'


@register.filter
def gravatar_url(email: str, size: int = 55) -> str:
    """Get gravatar URL for an account.

    Args:
        email: str - account email.
        size: int, optional - avatar size. Defaults to 55.

    Returns:
        str: avatar url.
    """
    default = DEFAULT
    email_encoded = email.lower().encode('utf-8')
    email_hash = hashlib.sha256(email_encoded).hexdigest()
    url_params = urlencode({'d': default, 's': str(size)})
    return f'https://www.gravatar.com/avatar/{email_hash}?{url_params}'


@register.filter
def get_avatar(user: Account) -> str:
    """Get avatar for Account.

    Args:
        user: Account - account for find avatar.

    Returns:
        str: avatar url.
    """
    if user.avatar:
        return user.avatar.url
    return gravatar_url(user.email)


@register.filter
def get_tour_cover(tour: Tour) -> str:
    """Get tour cover.

    Args:
        tour: Tour - tour for find cover.

    Returns:
        str: cover url.
    """
    if tour.avatar:
        return tour.avatar.url
    return DEFAULT
