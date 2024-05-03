from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


NAME_MAX_LEN = 255


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