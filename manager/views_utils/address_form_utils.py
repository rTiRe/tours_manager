from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.template.loader import render_to_string
from ..models import Address
from ..forms import AddressFormForCreate
from . import convert_errors


def render_address_form(
    request: HttpRequest,
    literals: dict,
) -> str | HttpResponseRedirect:
    errors = {}
    next = request.GET.get('next', reverse('my_profile'))
    next = request.POST.get('next', next)
    if request.method == 'POST':
        form = AddressFormForCreate(data=request.POST)
        if form.is_valid():
            Address.objects.create(**form.cleaned_data)
            return redirect(next)
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    form = AddressFormForCreate()
    return render_to_string(
        'parts/address_form.html',
        {
            'next': next,
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