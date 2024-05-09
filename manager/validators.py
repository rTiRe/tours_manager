from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import models, password_validation
from django.http import QueryDict
from rest_framework.request import Empty
from typing import Any
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


def password_validator(password: str, password2: str) -> None:
    check_empty(password)
    check_str(password)
    password = str(password)
    password_validation.validate_password(password)
    password2 = str(password2)
    if password != password2:
        raise ValidationError(
            _('password and password2 must be the same!'),
            params={'password': password}
        )


def user_fields_validator(data: Empty | dict | QueryDict | Any) -> None:
    user_fields = 'username', 'first_name', 'last_name', 'email', 'password', 'password2'
    set_user_keys = set(user_fields)
    data_fields = data.keys()
    if not set_user_keys.issubset(data_fields):
        keys = list(set_user_keys - set(data_fields))
        response_dict = {key: _('field must be present') for key in keys}
        raise ValidationError(str(response_dict))


def username_validator(username: str, ignore_existing_username: bool = False) -> None:
    check_empty(username)
    check_str(username)
    rule = re.compile(r'^[a-z][a-z_0-9]*[^_]$')
    if not rule.search(username):
        raise ValidationError(
            contains_illegal_characters,
            params={'username': username}
        )
    if models.User.objects.filter(username=username).exists() and not ignore_existing_username:
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
