"""Admin panel fields."""

from django.contrib import admin

from .forms import AddressForm, ReviewForm
from .models import (Account, Address, Agency, AgencyRequests, City, Country,
                     Review, Tour, TourAddress)

name = 'name'
agency = 'agency'
account = 'account'


class TourCityInline(admin.TabularInline):
    """Inline for Country and Tour link."""

    model = TourAddress
    extra = 0
    min_num = 1


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    """Agency field for admin panel."""

    model = Agency
    list_display = [name, 'phone_number']
    search_fields = [name, 'phone_number']
    list_filter = [name, 'phone_number']
    autocomplete_fields = ['address']


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    """Tour field for admin panel."""

    model = Tour
    list_display = [name, 'description']
    search_fields = [name, 'description']
    list_filter = [name]
    autocomplete_fields = ['agency']
    inlines = (TourCityInline,)


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Country field for admin panel."""

    model = Country
    list_display = [name]
    search_fields = [name]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """City field for admin panel."""

    model = City
    list_display = [name, 'country']
    search_fields = [name, 'country']
    autocomplete_fields = ['country']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Address field for admin panel."""

    model = Address
    list_display = [
        'city',
        'street',
        'house_number',
        'entrance_number',
        'floor',
        'flat_number',
    ]
    search_fields = ['city', 'street', 'house_number']
    autocomplete_fields = ['city']
    form = AddressForm


@admin.register(TourAddress)
class TourAddressAdmin(admin.ModelAdmin):
    """Field tour and city link for admin panel."""

    model = TourAddress


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review field for admin panel."""

    model = Review
    list_display = [
        'tour',
        account,
        'rating',
        'text',
    ]
    search_fields = [
        'tour',
        account,
        'rating',
    ]
    autocomplete_fields = [
        'tour',
        account,
    ]
    form = ReviewForm


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Account field for admin panel."""

    model = Account
    list_display = [account]
    search_fields = [account]


@admin.register(AgencyRequests)
class AgencyRequestsAdmin(admin.ModelAdmin):
    model = AgencyRequests
