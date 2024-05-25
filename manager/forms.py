"""Classes with changed forms."""

from django import forms

from .models import Address, Review, Tour, Agency
from django.contrib.auth import forms as auth_forms, models
from django.http import HttpRequest

from django.utils.translation import gettext_lazy as _

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
        tours_addresses = [tour.addresses.all() for tour in tours_objects]
        tours_countries_objects = set()
        for address_objects in tours_addresses:
            for address_object in address_objects:
                country_object = address_object.city.country
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


class FindAgenciesForm(forms.Form):
    city = forms.ChoiceField(required=False)

    def __init__(self, request: HttpRequest = None, *args, **kwargs):
        super(FindAgenciesForm, self).__init__(*args, **kwargs)
        city_choice_list = [('', _('all'))]
        agencies_objects = Agency.objects.all()
        agencies_cities = [agency.address.city for agency in agencies_objects.all()]
        city_choice_list += [(city.id, city.name) for city in agencies_cities]
        self.fields['city'].choices = city_choice_list
        if request and request.method == 'GET':
            self.fields['city'].initial = request.GET.get('city')


class SignupForm(auth_forms.UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class SigninForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)