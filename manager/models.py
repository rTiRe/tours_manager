from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


NAME_MAX_LEN = 255
PHONE_NUMBER_MAX_LEN = 12


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
        null = False,
        blank = False,
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
    )
    rating = models.FloatField(
        _('rating'),
        null=False,
        blank=False
    )

    def __str__(self) -> None:
        return self.name

    class Meta:
        db_table = '"tours_data"."agency"'
        ordering = ['name']
        verbose_name = _('agency')
        verbose_name_plural = _('agencies')
        unique_together = (('name',),)
