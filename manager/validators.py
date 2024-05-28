"""Module with fields validators."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from datetime import datetime, timezone

contains_illegal_characters = _('field contains illegal characters.')


def get_datetime():
    return datetime.now(timezone.utc)


def street_name_validator(name: str) -> None:
    """Validate street name.

    Args:
        name: str - street name.

    Raises:
        ValidationError: if name contains incorrect format.
    """
    rule = re.compile('^[а-яА-ЯёЁa-zA-Z0-9 ]+$')
    if not rule.search(name):
        raise ValidationError(
            _('Street name contains incorrect symbols.'),
            params={'street_name': name},
        )


def house_number_validator(number: str) -> None:
    """Validate house number.

    Args:
        number: str - house number.

    Raises:
        ValidationError: if number contains incorrect format.
    """
    rule = re.compile(r'^[1-9]\d*(?: ?(?:([а-яА-Яa-zA-Z])|[\/-] ?[1-9]+\d*([а-яА-Яa-zA-Z])?))?$')
    if not rule.search(number):
        message = 'Incorrect house number format. Use one of this'
        correct_fields = '12, 12а, 12А, 12 А, 12 а, 56/58, 56/58а, 56-58, 56 - 58, 56-58а'
        raise ValidationError(
            _(f'{message}:\n {correct_fields}'),
            params={'house_number': number},
        )


def phone_number_validator(number: str) -> None:
    """Validate phone number.

    Args:
        number: str - phone_number.

    Raises:
        ValidationError: if phone number contains incorrect format.
    """
    rule = re.compile(r'^\+7[0-9]{3}[0-9]{7}$')
    if not rule.search(number):
        raise ValidationError(
            _('Number must be in format +79999999999'),
            params={'phone_number': number},
        )


def check_empty(field: str) -> None:
    """Check is field empty.

    Args:
        field: str - field to check.

    Raises:
        ValueError: if field is empty.
    """
    if not field:
        raise ValueError(_("field can't be empty!"))


def check_str(field: str) -> None:
    """Check is field instance str.

    Args:
        field: str - field to check.

    Raises:
        TypeError: if field not instance str.
    """
    if not isinstance(field, str):
        field_type = type(field).__name__
        raise TypeError(_(f'field must be string, not {field_type}'))


def date_validator(date: datetime) -> None:
    if not isinstance(date, datetime):
        field_type = type(date).__name__
        raise TypeError(_(f'Field must be datetime, not {field_type}'))
    if date > get_datetime():
        raise ValueError(_(f'Time cannot be in future.'))
