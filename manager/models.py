from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


NAME_MAX_LEN = 255
PHONE_NUMBER_MAX_LEN = 12


def phone_number_validator(number: str) -> None:
    import re
    rule = re.compile(r'^\+7[0-9]{3}[0-9]{7}$')
    if not rule.search(number):
        raise ValidationError(
            _('Number must be in format +79999999999'),
            params={'phone_number': number}
        )


class UUIDMixin(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(
        verbose_name = _('name'),
        max_length = NAME_MAX_LEN
    )

    class Meta:
        abstract = True


class Agency(UUIDMixin, NameMixin, models.Model):
    phone_number = models.CharField(
        _('phone number'),
        null=False,
        blank=False,
        max_length=PHONE_NUMBER_MAX_LEN,
        validators=[phone_number_validator]
    )

    def __str__(self) -> None:
        return self.name

    class Meta:
        db_table = '"tours_data"."agency"'
        ordering = ['name']
        verbose_name = _('agency')
        verbose_name_plural = _('agencies')
        unique_together = (('name',),)


class Tour(UUIDMixin, NameMixin, models.Model):
    description = models.TextField(_('description'))
    agency = models.ForeignKey(
        Agency,
        verbose_name=_('agency'),
        on_delete=models.CASCADE
    )

    def __str__(self) -> None:
        return self.name

    class Meta:
        db_table = '"tours_data"."tour"'
        ordering = ['name']
        verbose_name = _('tour')
        verbose_name_plural = _('tours')
        unique_together = (('name', 'description', 'agency'),)