from django.contrib import admin
from .models import Agency, Tour, City, TourCity


class TourCityInline(admin.TabularInline):
    model = TourCity
    extra = 0
    min_num = 1


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    model = Agency
    list_display = ['name', 'phone_number']
    search_fields = ['name', 'phone_number']
    list_filter = ('name', 'phone_number')


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    model = Tour
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    list_filter = ('name',)
    inlines = (TourCityInline,)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    model = City
    list_display = ['name', 'country']
    search_fields = ['name', 'country']


@admin.register(TourCity)
class TourCityAdmin(admin.ModelAdmin):
    model = TourCity
