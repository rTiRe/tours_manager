"""Module with functions for work with address form."""

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse

from ..forms import AddressFormForCreate
from ..models import Address
from .errors_utils import convert_errors


def render_address_form(
    request: HttpRequest,
    literals: dict,
) -> str | HttpResponseRedirect:
    """Pretty render address form.

    Args:
        request: HttpRequest - user request.
        literals: dict - literals for paste in form.

    Returns:
        str | HttpResponseRedirect: rendered form or redirect if address created.
    """
    errors = {}
    next_page = request.GET.get('next', reverse('my_profile'))
    next_page = request.POST.get('next', next_page)
    if request.method == 'POST':
        form = AddressFormForCreate(data=request.POST)
        if form.is_valid():
            Address.objects.create(**form.cleaned_data)
            return redirect(next_page)
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    form = AddressFormForCreate()
    return render_to_string(
        'parts/address_form.html',
        {
            'next': next_page,
            'address_form': form,
            'errors': errors,
            'title': literals.get('title'),
            'button': literals.get('button'),
            'button_name': literals.get('button_name'),
            'style_files': [
                'css/account_form.css',
                'css/settings.css',
                'css/tour_form.css',
            ],
        },
        request=request,
    )
