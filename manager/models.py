"""Module with table models."""

from uuid import uuid4

from django.conf.global_settings import AUTH_USER_MODEL
from django.contrib.gis.db import models as gismodels
from django.db import models
from django.utils.translation import gettext_lazy as _

from .validators import (house_number_validator, phone_number_validator,
                         street_name_validator)

NAME_MAX_LEN = 255
PHONE_NUMBER_MAX_LEN = 12
COUNTRY_MAX_LEN = 255
STREET_MAX_LEN = 255
HOUSE_NUMBER_MAX_LEN = 8
REVIEW_TEXT_MAX_LEN = 8192
srid = 4326

name_field = 'name'
agency_field = 'agency'
country_field = 'country'
city_field = 'city'


class UUIDMixin(models.Model):
    """Create id field with default UUID vaule."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
    )

    class Meta:
        """Meta class with Mixin settings."""

        abstract = True


class NameMixin(models.Model):
    """Create name field."""

    name = models.CharField(
        verbose_name=_(name_field),
        max_length=NAME_MAX_LEN,
    )

    class Meta:
        """Meta class with Mixin settings."""

        abstract = True


class Country(UUIDMixin, models.Model):
    """Country table model."""

    name = models.CharField(
        _(country_field),
        max_length=COUNTRY_MAX_LEN,
        unique=True,
    )

    def __str__(self) -> str:
        """Stringify class.

        Returns:
            str: stringified class. Name.
        """
        return self.name

    class Meta:
        """Meta class with Country settings."""

        db_table = '"tours_data"."country"'
        verbose_name = _('country')
        verbose_name_plural = _('countries')


class City(UUIDMixin, NameMixin, models.Model):
    """City table model."""

    country = models.ForeignKey(
        Country,
        verbose_name=_(country_field),
        on_delete=models.CASCADE,
    )
    point = gismodels.PointField(
        _('city geopoint'),
        srid=srid,
        unique=True,
    )

    def __str__(self) -> None:
        """Stringify class.

        Returns:
            str: stringified class. Name, country.
        """
        return f'{self.name}, {self.country}'

    class Meta:
        """Meta class with City settings."""

        db_table = '"tours_data"."city"'
        verbose_name = _(city_field)
        verbose_name_plural = _('cities')
        unique_together = (
            (
                name_field,
                country_field,
            ),
        )


class Address(UUIDMixin, models.Model):
    """Address table model."""

    city = models.ForeignKey(
        City,
        verbose_name=_(city_field),
        on_delete=models.CASCADE,
    )
    street = models.CharField(
        _('street name'),
        max_length=STREET_MAX_LEN,
        validators=[street_name_validator],
    )
    house_number = models.CharField(
        _('house number'),
        max_length=HOUSE_NUMBER_MAX_LEN,
        validators=[house_number_validator],
    )
    entrance_number = models.SmallIntegerField(
        _('entrance number'),
        null=True,
        blank=True,
    )
    floor = models.SmallIntegerField(
        _('floor number'),
        null=True,
        blank=True,
    )
    flat_number = models.SmallIntegerField(
        _('flat number'),
        null=True,
        blank=True,
    )
    point = gismodels.PointField(
        _('address geopoint'),
        srid=srid,
    )
    tours = models.ManyToManyField(
        'Tour',
        verbose_name=_('tours'),
        through='TourAddress',
    )

    def __str__(self) -> str:
        """Stringify class.

        Returns:
            str: stringified class. Not_nul_part can_be_null_part.
        """
        not_null_part = ' '.join([self.city.name, self.street, self.house_number])
        can_be_null_parts = ' '.join(
            [
                str(self.entrance_number),
                str(self.floor),
                str(self.flat_number),
            ],
        )
        return f'{not_null_part} {can_be_null_parts}'.strip()

    class Meta:
        """Meta class with Address settings."""

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


class Agency(UUIDMixin, NameMixin, models.Model):
    """Agency model."""

    phone_number = models.CharField(
        _('phone number'),
        max_length=PHONE_NUMBER_MAX_LEN,
        validators=[phone_number_validator],
    )
    address = models.OneToOneField(
        'Address',
        verbose_name=_('address'),
        unique=True,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        """Stringify class.

        Returns:
            str: stringified class. Name, phone_number.
        """
        return f'{self.name}, {self.phone_number}'

    class Meta:
        """Meta class with Agency settings."""

        db_table = '"tours_data"."agency"'
        ordering = [name_field]
        verbose_name = _(agency_field)
        verbose_name_plural = _('agencies')
        unique_together = ((name_field,),)


class Tour(UUIDMixin, NameMixin, models.Model):
    """Tour table model."""

    description = models.TextField(_('description'))
    agency = models.ForeignKey(
        Agency,
        verbose_name=_(agency_field),
        on_delete=models.CASCADE,
    )
    addresses = models.ManyToManyField(
        'Address',
        verbose_name=_('address'),
        through='TourAddress',
    )
    starting_city = models.ForeignKey(
        'City',
        verbose_name=_('starting city'),
        on_delete=models.CASCADE,
    )
    price = models.DecimalField(
        _('price'),
        max_digits = 9,
        decimal_places = 2,
    )

    def __str__(self) -> str:
        """Stringify class.

        Returns:
            str: stringified class. Name, agency.
        """
        return f'{self.name}, {self.agency}'

    class Meta:
        """Meta class with Tour settings."""

        db_table = '"tours_data"."tour"'
        ordering = [name_field]
        verbose_name = _('tour')
        verbose_name_plural = _('tours')
        unique_together = ((name_field, 'description', agency_field),)


class TourAddress(UUIDMixin, models.Model):
    """Model for Tour and City tables link."""

    tour = models.ForeignKey(Tour, verbose_name=_('tour'), on_delete=models.CASCADE)
    address = models.ForeignKey(Address, verbose_name=_('address'), on_delete=models.CASCADE)

    class Meta:
        """Meta class with Tour settings."""

        db_table = '"tours_data"."tour_address"'
        unique_together = (('tour', 'address'),)
        verbose_name = _('relationship tour address')
        verbose_name_plural = _('relationships tour address')


class Review(UUIDMixin, models.Model):
    """Review table model."""

    tour = models.ForeignKey(
        Tour,
        verbose_name=_('tour'),
        on_delete=models.CASCADE,
    )
    account = models.ForeignKey(
        'Account',
        verbose_name=_('account'),
        on_delete=models.CASCADE,
    )
    rating = models.FloatField(
        _('rating'),
    )
    text = models.TextField(
        _('text'),
        max_length=REVIEW_TEXT_MAX_LEN,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        """Stringify class.

        Returns:
            str: stringified class. Rating (Username for agency).
        """
        rating = self.rating
        username = self.account.username
        tour = self.tour
        return f'{rating} ({username}) for {tour}'  

    class Meta:
        """Meta class with Review settings."""

        db_table = '"tours_data"."review"'
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        unique_together = (('tour', 'account'),)


class Account(UUIDMixin, models.Model):
    """Account table model."""

    account = models.OneToOneField(
        AUTH_USER_MODEL,
        unique=True,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    agency = models.OneToOneField(
        Agency,
        verbose_name=_('agency account'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        unique=True,
        related_name='account',
    )

    class Meta:
        """Meta class with Account settings."""

        db_table = '"tours_data"."account"'
        verbose_name = _('account')
        verbose_name_plural = _('accounts')

    def __str__(self) -> str:
        """Stringify class.

        Returns:
            str: stringified class.Username (first_name last_name)
        """
        username = self.account.username
        first_name = self.account.first_name
        last_name = self.account.last_name
        return f'{username} ({first_name} {last_name})'

    @property
    def username(self) -> str:
        """Get username.

        Returns:
            str: account username.
        """
        return self.account.username

    @property
    def first_name(self) -> str:
        """Get first_name.

        Returns:
            str: account first name.
        """
        return self.account.first_name

    @property
    def last_name(self) -> str:
        """Get last_name.

        Returns:
            str: account last name.
        """
        return self.account.last_name

    @property
    def email(self) -> str:
        """Get email.

        Returns:
            str: account email.
        """
        return self.account.email
