"""Classes with changed forms."""

from django import forms
from django.contrib.gis import forms as gis_forms
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from .models import Address, Agency, Review, Tour

name_min = 'min'
name_max = 'max'
name_step = 'step'
address_widgets = {
    'entrance_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
    'floor': forms.NumberInput(attrs={name_min: -1, name_step: 1}),
    'flat_number': forms.NumberInput(attrs={name_min: 1, name_step: 1}),
    'point': gis_forms.OSMWidget(attrs={'map_width': 800, 'map_height': 500}),
}
ALL_LITERAL = '__all__'
CITY_LITERAL = 'city'


class CustomImageInput(forms.ClearableFileInput):
    """Class for customize image input view."""

    template_name = 'image_input.html'


class AddressForm(forms.ModelForm):
    """Class for address form."""

    class Meta:
        """Form meta class with settings."""

        model = Address
        fields = ALL_LITERAL
        widgets = address_widgets


class AddressFormForCreate(AddressForm):
    """Form for create address."""

    class Meta:
        """Address Form Meta class."""

        model = Address
        fields = [
            CITY_LITERAL,
            'street',
            'house_number',
            'entrance_number',
            'floor',
            'flat_number',
            'point',
        ]
        widgets = address_widgets


class ReviewForm(forms.ModelForm):
    """Form for create review in admin."""

    rating_choices = [
        (5, '5 звезд'),
        (4, '4 звезды'),
        (3, '3 звезды'),
        (2, '2 звезды'),
        (1, '1 звезда'),
    ]
    rating = forms.ChoiceField(
        choices=rating_choices,
        widget=forms.RadioSelect(attrs={'class': 'rating rating_input'}),
        label=_('Rating'),
    )
    text = forms.CharField(
        widget=forms.Textarea,
        label=_('Text'),
        max_length=1000,
    )

    def my_render(self, request: HttpRequest, review: Review = None) -> str:
        """Render form.

        Args:
            request: HttpRequest - request from user.
            review: Review, optional - review for init data. Defaults to None.

        Returns:
            str: rendered form.
        """
        if review:
            button_icon = 'fa-save'
            button_literal = _('Save')
        else:
            button_icon = 'fa-plus'
            button_literal = _('Create')
        return render_to_string(
            'parts/review_form.html',
            {
                'form': self,
                'button_icon': button_icon,
                'button_literal': button_literal,
                'style_files': [
                    'css/review_create.css',
                    'css/rating.css',
                ],
            },
            request=request,
        )

    class Meta:
        """Form Meta class."""

        model = Review
        fields = ALL_LITERAL


class UserReviewForm(ReviewForm):
    """Form for create review on site."""

    class Meta:
        """User Form Meta class."""

        model = Review
        fields = ['rating', 'text']


class FindToursForm(forms.Form):
    """Form for find tours."""

    country = forms.ChoiceField(required=True)
    starting_city = forms.ChoiceField(required=True)

    def __init__(self, request: HttpRequest = None, *args, **kwargs):
        """Init default form data.

        Args:
            request: HttpRequest - request from user. Default to None.
            args: args.
            kwargs: kwargs.
        """
        super().__init__(*args, **kwargs)
        starting_city_choice_list, country_choice_list = [('', '')], [('', '')]
        tours_objects = Tour.objects.all()
        tours_starting_city = list({tour.starting_city for tour in tours_objects})
        tours_addresses = [tour.addresses.all() for tour in tours_objects]
        tours_countries_objects = set()
        for address_objects in tours_addresses:
            for address_object in address_objects:
                tours_countries_objects.add(address_object.city.country)
        tours_starting_city = sorted(
            tours_starting_city, key=lambda country: country.name,
        )
        tours_countries_objects = list(set(tours_countries_objects))
        tours_countries_objects = sorted(
            tours_countries_objects, key=lambda country: country.name,
        )
        starting_city_choice_list += [(city.id, city.name) for city in tours_starting_city]
        country_choice_list += [(country.id, country.name) for country in tours_countries_objects]
        self.fields['starting_city'].choices = starting_city_choice_list
        self.fields['country'].choices = country_choice_list
        if request and request.method == 'GET':
            self.fields['country'].initial = request.GET.get('country')
            self.fields['starting_city'].initial = request.GET.get('starting_city')


class FindAgenciesForm(forms.Form):
    """Form for find agencies."""

    city = forms.ChoiceField(required=False)

    def __init__(self, request: HttpRequest = None, *args, **kwargs):
        """Init.

        Args:
            request: HttpRequest - request from user. Default to None.
            args: args.
            kwargs: kwargs.
        """
        super().__init__(*args, **kwargs)
        city_choice_list = [('', _('all'))]
        agencies_objects = Agency.objects.all()
        agencies_cities = [agency.address.city for agency in agencies_objects.all()]
        city_choice_list += [(city.id, city.name) for city in agencies_cities]
        city_choice_list = list(set(city_choice_list))
        self.fields[CITY_LITERAL].choices = city_choice_list
        if request and request.method == 'GET':
            self.fields[CITY_LITERAL].initial = request.GET.get(CITY_LITERAL)


class TourForm(forms.ModelForm):
    """For for Tour."""

    addresses = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple)
    avatar = forms.ImageField(required=False, widget=CustomImageInput)

    def __init__(self, *args, **kwargs) -> None:
        """Init.

        Args:
            args: args.
            kwargs: kwargs.
        """
        address_choices = []
        addresses = Address.objects.all()
        for address in addresses:
            address_choices.append((address.id, str(address)))
        super().__init__(*args, **kwargs)
        self.fields['addresses'].choices = address_choices

    class Meta:
        """Form Meta class."""

        model = Tour
        fields = ALL_LITERAL


class TourEditForm(TourForm):
    """For for edit tour."""

    def clean(self) -> dict:
        """Form clean method.

        Returns:
            dict: cleaned data.
        """
        name = self.cleaned_data.get('name')
        description = self.cleaned_data.get('description')
        agency = self.cleaned_data.get('agency')
        tour = Tour.objects.filter(name=name, description=description, agency=agency)
        if tour.exclude(id=self.instance.id).exists():
            fields = ['Name', 'Description', 'Agency']
            fields = ', '.join(fields)
            error = f'A tour with the following values ​​for the {fields} fields already exists.'
            self.add_error(
                ALL_LITERAL,
                _(error),
            )
        else:
            return self.cleaned_data
