"""Classes with changed forms."""

from django import forms

from .models import Address, Review

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
