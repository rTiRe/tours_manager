"""Classes with changed forms."""

from django import forms

from .models import Address, Review, Tour
from django.http import HttpRequest

name_min = 'min'
name_max = 'max'
name_step = 'step'


class AddressForm(forms.ModelForm):
    """Class for address form."""

    class Meta:
        """Form meta class with settings."""

        model = Address
        fields = '__all__'
        widgets = {
            'entrance_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
            'floor': forms.NumberInput(attrs={name_min: -1, name_step: 1}),
            'flat_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
        }


class ReviewForm(forms.ModelForm):
    """Class for review form."""

    class Meta:
        """Form meta class with settings."""

        model = Review
        fields = '__all__'
        widgets = {
            'rating': forms.NumberInput(attrs={name_min: 1, name_max: 5, name_step: 0.1}),
        }


class FindToursForm(forms.Form):
    country = forms.ChoiceField(required=True)
    starting_city = forms.ChoiceField(required=True)

    def __init__(self, request: HttpRequest = None, *args, **kwargs):
        super(FindToursForm, self).__init__(*args, **kwargs)
        starting_city_choice_list, country_choice_list = [('', '')], [('', '')]
        tours_objects = Tour.objects.all()
        tours_starting_city = [tour.starting_city for tour in tours_objects]
        tours_countries = [tour.countries.all() for tour in tours_objects]
        tours_countries_objects = set()
        for tour_countries in tours_countries:
            for country_object in tour_countries.all():
                if country_object:
                    tours_countries_objects.add(country_object)
        tours_starting_city = sorted(list(set(tours_starting_city)), key=lambda x: x.name)
        tours_countries_objects = sorted(list(set(tours_countries_objects)), key=lambda x: x.name)
        starting_city_choice_list += [(city.id, city.name) for city in tours_starting_city]
        country_choice_list += [(country.id, country.name) for country in tours_countries_objects]
        self.fields['starting_city'].choices = starting_city_choice_list
        self.fields['country'].choices = country_choice_list
        if request and request.method == 'GET':
            self.fields['country'].initial = request.GET.get('country')
            self.fields['starting_city'].initial = request.GET.get('starting_city')