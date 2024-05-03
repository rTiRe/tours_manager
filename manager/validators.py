from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import re

COUNTRIES = []

def street_name_validator(name: str) -> None:
    rule = re.compile(r'^[^\W\d_]+\.?(?:[-\s\'’][^\W\d_]+\.?)*$')
    if not rule.search(name):
        raise ValidationError(
            _('Street name contains incorrect symbols.'),
            params={'street_name': name}
        )


def house_number_validator(number: str) -> None:
    rule = re.compile(r'^[1-9]\d*(?: ?(?:([а-я]|[a-z])|[/-] ?\d+([а-я]|[a-z])?))?$')
    if not rule.search(number):
        raise ValidationError(
            _("""Incorrect house number format. Use one of this:
12, 12а, 12А,12 А, 12 а, 12 б, 12 я, 121 б, 56/58, 56/58а, 56-58, 56 - 58, 56-58а"""),
            params={'house_number': number}
        )


def country_validator(country: str) -> None:
    if not COUNTRIES:
        import os
        import csv
        file_path = f'{os.getcwd()}/countries.csv'
        with open(file_path, 'r', encoding='utf-8') as countries_csv:
            reader = csv.reader(countries_csv)
            COUNTRIES.extend(next(reader))
    if country not in COUNTRIES:
        raise ValidationError(
            _('This country does not exists.'),
            params={'country': country}
        )
        


def phone_number_validator(number: str) -> None:
    rule = re.compile(r'^\+7[0-9]{3}[0-9]{7}$')
    if not rule.search(number):
        raise ValidationError(
            _('Number must be in format +79999999999'),
            params={'phone_number': number}
        )