"""Classes with changed forms."""

from django import forms
from django.contrib.gis import forms as gis_forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import models as auth_models
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import Address, Agency, Review, Tour, Account
from django.contrib.auth.password_validation import validate_password

name_min = 'min'
name_max = 'max'
name_step = 'step'

ADDRESS_WIDGETS = {
        'entrance_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
        'floor': forms.NumberInput(attrs={name_min: -1, name_step: 1}),
        'flat_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
        'point': gis_forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}),
    }


class AddressForm(forms.ModelForm):
    """Class for address form."""

    class Meta:
        """Form meta class with settings."""

        model = Address
        fields = '__all__'
        widgets = ADDRESS_WIDGETS


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, '5 звезд'),
        (4, '4 звезды'),
        (3, '3 звезды'),
        (2, '2 звезды'),
        (1, '1 звезда'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating rating_input'}),
    )
    text = forms.CharField(
        widget=forms.Textarea,
    )
    
    class Meta:
        model = Review
        fields = '__all__'


class UserReviewForm(ReviewForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']


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
        city_choice_list = list(set(city_choice_list))
        self.fields['city'].choices = city_choice_list
        if request and request.method == 'GET':
            self.fields['city'].initial = request.GET.get('city')


class SignupForm(auth_forms.UserCreationForm):
    email = forms.EmailField(required=True)
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    def clean(self):
        email = self.cleaned_data.get('email')
        if auth_models.User.objects.filter(email=email).exists():
            self.add_error('email', _('Email currently exists.'))
        return self.cleaned_data

    class Meta:
        model = auth_models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class SigninForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SettingsUserForm(auth_forms.UserChangeForm):
    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False)

    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        super(SettingsUserForm, self).__init__(*args, **kwargs)
        self.request = request
        del self.fields['password']
        if self.request and isinstance(self.request, HttpRequest):
            user = self.request.user
            account = Account.objects.filter(account=user).first()
            if account and account.avatar:
                self.fields['avatar'].initial = account.avatar
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
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar']


class SettingsAgencyForm(forms.ModelForm):
    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        super(SettingsAgencyForm, self).__init__(*args, **kwargs)
        if request and isinstance(request, HttpRequest):
            user = Account.objects.get(account=request.user.id)
            self.fields['name'].initial = user.agency.name
            self.fields['phone_number'].initial = user.agency.phone_number

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Agency.objects.filter(name=name).exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Это имя уже занято другим агентством.')
        return name

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


class TourForm(forms.ModelForm):
    addresses = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple)
    def __init__(self, *args, **kwargs) -> None:
        address_choices = []
        addresses = Address.objects.all()
        for address in addresses:
            address_choices.append((address.id, str(address)))
        super(TourForm, self).__init__(*args, **kwargs)
        self.fields['addresses'].choices = address_choices

    class Meta:
        model = Tour
        fields = '__all__'


class TourEditForm(TourForm):
    def __init__(self, *args, **kwargs) -> None:
        super(TourEditForm, self).__init__(*args, **kwargs)
    def clean(self):
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        agency = self.cleaned_data.get('agency')
        if Tour.objects.filter(
            name=name,
            description=description,
            agency=agency,
        ).exclude(id=self.instance.id).exists():
            fields = ['Name', 'Description', 'Agency']
            error = f'A tour with the following values ​​for the\
                {", ".join(fields)} fields already exists.'
            self.add_error(
                '__all__',
                _(error),
            )
        else:
            return self.cleaned_data


class PasswordChangeRequestForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        validate_password(new_password)

        if new_password != new_password_confirm:
            raise forms.ValidationError(_('Passwords do not match.'))
        
        return cleaned_data
