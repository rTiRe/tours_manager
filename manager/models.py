from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _

from .validators import phone_number_validator, country_validator, \
    street_name_validator, house_number_validator


NAME_MAX_LEN = 255
PHONE_NUMBER_MAX_LEN = 12
COUNTRY_MAX_LEN = 255
STREET_MAX_LEN = 255
HOUSE_NUMBER_MAX_LEN = 8
REVIEW_TEXT_MAX_LEN = 8192


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
        max_length=PHONE_NUMBER_MAX_LEN,
        validators=[phone_number_validator]
    )
    address = models.OneToOneField(
        'Address',
        verbose_name=_('address'),
        unique=True,
        on_delete=models.CASCADE
    )

    def __str__(self) -> None:
        return f'{self.name}, {self.phone_number}'

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
    cities = models.ManyToManyField(
        'City',
        verbose_name=_('cities'),
        through='TourCity'
    )

    def __str__(self) -> None:
        return f'{self.name}, {self.agency}'

    class Meta:
        db_table = '"tours_data"."tour"'
        ordering = ['name']
        verbose_name = _('tour')
        verbose_name_plural = _('tours')
        unique_together = (('name', 'description', 'agency'),)


class City(UUIDMixin, NameMixin, models.Model):
    country = models.CharField(
        _('country'),
        max_length=COUNTRY_MAX_LEN,
        validators=[country_validator]
    )
    tours = models.ManyToManyField(
        'Tour',
        verbose_name=_('tours'),
        through='TourCity'
    )

    def __str__(self) -> None:
        return f'{self.name}, {self.country}'

    class Meta:
        db_table = '"tours_data"."city"'  
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        unique_together = (('name', 'country'),)


class TourCity(UUIDMixin, models.Model):
    tour = models.ForeignKey(Tour, verbose_name=_('tour'), on_delete=models.CASCADE)
    city = models.ForeignKey(City, verbose_name=_('city'), on_delete=models.CASCADE)

    class Meta:
        db_table = '"tours_data"."tour_city"'
        unique_together = (('tour', 'city'),)
        verbose_name = _('relationship tour city')
        verbose_name_plural = _('relationships tour city')


class Address(UUIDMixin, models.Model):
    city = models.ForeignKey(
        City,
        verbose_name=_('city'),
        on_delete=models.CASCADE
    )
    street = models.CharField(
        _('street name'),
        max_length=STREET_MAX_LEN,
        validators=[street_name_validator]
    )
    house_number = models.CharField(
        _('house number'),
        max_length=HOUSE_NUMBER_MAX_LEN,
        validators=[house_number_validator]
    )
    entrance_number = models.SmallIntegerField(
        _('entrance number'),
        null = True,
        blank = True,
    )
    floor = models.SmallIntegerField(
        _('floor number'),
        null = True,
        blank = True,
    )
    flat_number = models.SmallIntegerField(
        _('flat number'),
        null = True,
        blank = True,
    )


class Review(UUIDMixin, models.Model):
    agency_id = models.ForeignKey(
        Agency,
        verbose_name=_('agencies'),
        on_delete=models.CASCADE
    )
    rating = models.FloatField(
        _('rating'),
        validators=[]
    )
    text = models.TextField(
        _('text'),
        max_length=REVIEW_TEXT_MAX_LEN,
        null=True,
        blank=True
    )
