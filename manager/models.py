from django.db import models
from uuid import uuid4
from django.utils.translation import gettext_lazy as _
from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.gis.db import models as gismodels

from .validators import phone_number_validator, \
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

    def __str__(self) -> str:
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

    def __str__(self) -> str:
        return f'{self.name}, {self.agency}'

    class Meta:
        db_table = '"tours_data"."tour"'
        ordering = ['name']
        verbose_name = _('tour')
        verbose_name_plural = _('tours')
        unique_together = (('name', 'description', 'agency'),)


class Country(UUIDMixin, models.Model):
    name = models.CharField(
        _('country'),
        max_length=COUNTRY_MAX_LEN,
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = '"tours_data"."country"'
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class City(UUIDMixin, NameMixin, models.Model):
    country = models.ForeignKey(
        Country, 
        verbose_name=_('country'),
        on_delete=models.CASCADE
    )
    tours = models.ManyToManyField(
        'Tour',
        verbose_name=_('tours'),
        through='TourCity'
    )
    point = gismodels.PointField(
        _('city geopoint'),
        srid=4326,
        unique=True
    )

    def __str__(self) -> None:
        return f'{self.name}, {self.country}'

    class Meta:
        db_table = '"tours_data"."city"'  
        verbose_name = _('city')
        verbose_name_plural = _('cities')
        unique_together = (
            (
                'name',
                'country',
            ),
        )


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
    point = gismodels.PointField(
        _('address geopoint'),
        srid=4326,
    )

    def __str__(self) -> str:
        not_null_part = ' '.join([self.city.name, self.street, self.house_number])
        can_be_null_parts = ' '.join(
            [
                str(self.entrance_number),
                str(self.floor),
                str(self.flat_number)
            ]
        )
        return f'{not_null_part} {can_be_null_parts}'.strip()

    class Meta:
        db_table = '"tours_data"."address"'
        verbose_name = _('address')
        verbose_name_plural = _('addresses')
        unique_together = (
            (
                'city',
                'street',
                'house_number', 
                'entrance_number',
                'floor',
                'flat_number',
                'point',
            ),
        )


class Review(UUIDMixin, models.Model):
    agency = models.ForeignKey(
        Agency,
        verbose_name=_('agency'),
        on_delete=models.CASCADE
    )
    account = models.ForeignKey(
        'Account',
        verbose_name=_('account'),
        on_delete=models.CASCADE
    )
    rating = models.FloatField(
        _('rating'),
    )
    text = models.TextField(
        _('text'),
        max_length=REVIEW_TEXT_MAX_LEN,
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return _(f'{self.rating} ({self.account.username}) for {self.agency}')

    class Meta:
        db_table = '"tours_data"."review"'
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        unique_together = (('agency', 'account'),)


class Account(UUIDMixin, models.Model):
    account = models.OneToOneField(
        AUTH_USER_MODEL,
        unique=True,
        verbose_name=_('user'),
        on_delete=models.CASCADE
    )
    is_agency = models.BooleanField(
        _('agency account'),
    )

    class Meta:
        db_table = '"tours_data"."account"'
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def __str__(self) -> str:
        return f'{self.account.username} ({self.account.first_name} {self.account.last_name})'

    @property
    def username(self) -> str:
        return self.account.username

    @property
    def first_name(self) -> str:
        return self.account.first_name

    @property
    def last_name(self) -> str:
        return self.account.last_name
