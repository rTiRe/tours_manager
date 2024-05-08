from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import models
import re

contains_illegal_characters = _(f'field contains illegal characters.')

def street_name_validator(name: str) -> None:
    rule = re.compile(r'^[а-яА-ЯёЁa-zA-Z0-9 ]+$')
    if not rule.search(name):
        raise ValidationError(
            _('Street name contains incorrect symbols.'),
            params={'street_name': name}
        )


def house_number_validator(number: str) -> None:
    rule = re.compile(r'^[1-9]\d*(?: ?(?:([а-яА-Яa-zA-Z])|[\/-] ?[1-9]+\d*([а-яА-Яa-zA-Z])?))?$')
    if not rule.search(number):
        raise ValidationError(
            _("""Incorrect house number format. Use one of this:
12, 12а, 12А,12 А, 12 а, 12 б, 12 я, 121 б, 56/58, 56/58а, 56-58, 56 - 58, 56-58а"""),
            params={'house_number': number}
        )


def phone_number_validator(number: str) -> None:
    rule = re.compile(r'^\+7[0-9]{3}[0-9]{7}$')
    if not rule.search(number):
        raise ValidationError(
            _('Number must be in format +79999999999'),
            params={'phone_number': number}
        )


def check_empty(field: str) -> None:
    if not field:
        raise ValueError(_(f'field can\'t be empty!'))


def check_str(field: str) -> None:
    if not isinstance(field, str):
        raise TypeError(_(f'field must be string, not {type(field).__name__}'))


def username_validator(username: str) -> None:
        check_empty(username)
        check_str(username)
        rule = re.compile(r'^[a-z][a-z_0-9]*[^_]$')
        if not rule.search(username):
            raise ValidationError(
                contains_illegal_characters,
                params={'username': username}
            )
        if models.User.objects.filter(username=username).exists():
            raise ValidationError(
                _(f'{username} already exists!'),
                params={'username': username}
            )


def name_validator(name: str, type: str = None) -> None:
    check_empty(name)
    check_str(name)
    rule = re.compile(r'^[а-яА-ЯёЁa-zA-Z-]+$')
    if not rule.search(name):
        type = f'{type}_' if type else ''
        raise ValidationError(
            contains_illegal_characters,
            params={f'{type}name': name}
        )
