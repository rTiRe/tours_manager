"""Module with forms for profile."""

from django import forms
from django.contrib.auth import forms as auth_forms
from django.contrib.auth import models as auth_models
from django.contrib.auth.password_validation import validate_password
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from .forms import CustomImageInput, address_widgets
from .models import Account, Address, Agency

EMAIL_LITERAL = 'email'
USERNAME_LITERAL = 'username'


class SignupForm(auth_forms.UserCreationForm):
    """Signup form."""

    email = forms.EmailField(required=True)
    password1 = forms.PasswordInput()
    password2 = forms.PasswordInput()

    def clean(self) -> dict:
        """Signup Form clean method.

        Returns:
            dict: cleaned data.
        """
        email = self.cleaned_data.get(EMAIL_LITERAL)
        if auth_models.User.objects.filter(email=email).exists():
            self.add_error(EMAIL_LITERAL, _('Email currently exists.'))
        return self.cleaned_data

    class Meta:
        """Form Meta class."""

        model = auth_models.User
        fields = [
            USERNAME_LITERAL, 'first_name', 'last_name', EMAIL_LITERAL, 'password1', 'password2',
        ]


class SigninForm(forms.Form):
    """Signin form."""

    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class SettingsUserForm(auth_forms.UserChangeForm):
    """User settings form."""

    email = forms.EmailField(required=True)
    avatar = forms.ImageField(required=False, widget=CustomImageInput)

    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        """Init.

        Args:
            request: HttpRequest - request from user. Default to None.
            args: args.
            kwargs: kwargs.
        """
        super().__init__(*args, **kwargs)
        self.request = request
        self.fields.remove('password')
        if self.request and isinstance(self.request, HttpRequest):
            user = self.request.user
            account = Account.objects.filter(account=user).first()
            if account and account.avatar:
                self.fields['avatar'].initial = account.avatar
            self.fields[USERNAME_LITERAL].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields[EMAIL_LITERAL].initial = user.email

    def clean_username(self):
        """Clean username field from form.

        Raises:
            ValidationError: if username exists.

        Returns:
            str: username
        """
        username = self.cleaned_data.get(USERNAME_LITERAL)
        user = auth_models.User.objects.filter(username=username)
        if user.exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Это имя пользователя уже занято.')
        return username

    class Meta:
        """Settings User Form Meta class."""

        model = auth_models.User
        fields = [USERNAME_LITERAL, 'first_name', 'last_name', EMAIL_LITERAL, 'avatar']


class SettingsAgencyForm(forms.ModelForm):
    """Form for address settings."""

    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        """Init.

        Args:
            request: HttpRequest - request from user. Default to None.
            args: args.
            kwargs: kwargs.
        """
        super().__init__(*args, **kwargs)
        if request and isinstance(request, HttpRequest):
            user = Account.objects.get(account=request.user.id)
            if user.agency:
                self.fields['name'].initial = user.agency.name
                self.fields['phone_number'].initial = user.agency.phone_number

    def clean_name(self) -> str:
        """Clean name field from form.

        Raises:
            ValidationError: if name exists.

        Returns:
            str: name
        """
        name: str = self.cleaned_data.get('name')
        agency = Agency.objects.filter(name=name)
        if agency.exclude(id=self.instance.id).exists():
            raise forms.ValidationError('Это имя уже занято другим агентством.')
        return name

    class Meta:
        """Setting Agency Form Meta class."""

        model = Agency
        fields = ['name', 'phone_number']


class SettingsAddressForm(forms.ModelForm):
    """Form for address settings."""

    def __init__(self, request: HttpRequest = None, *args, **kwargs) -> None:
        """Set form initial data.

        Args:
            request: HttpRequest - request from user. Default to None.
            args: args.
            kwargs: kwargs.
        """
        super().__init__(*args, **kwargs)
        if request and isinstance(request, HttpRequest):
            user = Account.objects.get(account=request.user.id)
            if user.agency:
                self.fields['city'].initial = user.agency.address.city
                self.fields['street'].initial = user.agency.address.street
                self.fields['house_number'].initial = user.agency.address.house_number
                self.fields['entrance_number'].initial = user.agency.address.entrance_number
                self.fields['floor'].initial = user.agency.address.floor
                self.fields['flat_number'].initial = user.agency.address.flat_number
                self.fields['point'].initial = user.agency.address.point

    class Meta:
        """Settings Address Form Meta class."""

        model = Address
        fields = [
            'city', 'street', 'house_number', 'entrance_number', 'floor', 'flat_number', 'point',
        ]
        widgets = address_widgets


class PasswordChangeRequestForm(forms.Form):
    """For for the password change."""

    new_password = forms.CharField(widget=forms.PasswordInput)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput)

    def clean(self) -> dict:
        """Form clean method.

        Raises:
            ValidationError: if passwords do not match.

        Returns:
            dict: cleaned data.
        """
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')
        validate_password(new_password)
        if new_password != new_password_confirm:
            raise forms.ValidationError(_('Passwords do not match.'))
        return cleaned_data
