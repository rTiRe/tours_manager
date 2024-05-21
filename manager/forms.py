"""Classes with changed forms."""

from django import forms

from .models import Address, Review, City, Country

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
    country_choice_list, city_choice_list = [('', '')], [('', '')]
    city_objects = City.objects.all()
    country_choice_list += [(city.country.id, city.country.name) for city in city_objects]
    city_choice_list += [(city.id, city.name) for city in city_objects]
    country = forms.ChoiceField(choices=country_choice_list, required=True)
    city = forms.ChoiceField(choices=city_choice_list, required=True)
