"""Classes with changed forms."""

from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import models as auth_models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Address, Agency, Review, Tour, Account

name_min = 'min'
name_max = 'max'
name_step = 'step'

ADDRESS_WIDGETS = {
    'entrance_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
    'floor': forms.NumberInput(attrs={name_min: -1, name_step: 1}),
    'flat_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
}
REVIEW_WIDGETS = {
    'rating': forms.NumberInput(attrs={name_min: 1, name_max: 5, name_step: 0.1}),
}


class AddressForm(forms.ModelForm):
    """Class for address form."""

    class Meta:
        """Form meta class with settings."""

        model = Address
        fields = '__all__'
        widgets = ADDRESS_WIDGETS


class ReviewForm(forms.ModelForm):
    """Class for review form."""

    class Meta:
        """Form meta class with settings."""

        model = Review
        fields = '__all__'
        widgets = REVIEW_WIDGETS


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
        model = auth_models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class SigninForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SettingsUserForm(auth_forms.UserChangeForm):
    email = forms.EmailField(required=True)

    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        super(SettingsUserForm, self).__init__(*args, **kwargs)
        self.request = request
        del self.fields['password']
        if self.request and isinstance(self.request, HttpRequest):
            user = self.request.user
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if auth_models.User.objects.filter(username=username).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Это имя пользователя уже занято.')
        return username

    class Meta:
        model = auth_models.User
        fields = ['username', 'first_name', 'last_name', 'email']


class SettingsAgencyForm(forms.ModelForm):
    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        super(SettingsAgencyForm, self).__init__(*args, **kwargs)
        if request and isinstance(request, HttpRequest):
            user = Account.objects.get(account=request.user.id)
            self.fields['name'].initial = user.agency.name
            self.fields['phone_number'].initial = user.agency.phone_number

    class Meta:
        model = Agency
        fields = ['name', 'phone_number']


class SettingsAddressForm(forms.ModelForm):
    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        super(SettingsAddressForm, self).__init__(*args, **kwargs)
        if request and isinstance(request, HttpRequest):
            user = Account.objects.get(account=request.user.id)
            self.fields['city'].initial = user.agency.address.city
            self.fields['street'].initial = user.agency.address.street
            self.fields['house_number'].initial = user.agency.address.house_number
            self.fields['entrance_number'].initial = user.agency.address.entrance_number
            self.fields['floor'].initial = user.agency.address.floor
            self.fields['flat_number'].initial = user.agency.address.flat_number
            self.fields['point'].initial = user.agency.address.point
            

    class Meta:
        model = Address
        fields = ['city', 'street', 'house_number', 'entrance_number', 'floor', 'flat_number', 'point']
        widgets = ADDRESS_WIDGETS


class PasswordChangeRequestForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        new_password_confirm = cleaned_data.get("new_password_confirm")

        if new_password != new_password_confirm:
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
