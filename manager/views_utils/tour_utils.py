"""Module with functions for work with tours."""

from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string

from ..forms import TourEditForm, TourForm
from ..models import Agency, Tour
from .errors_utils import convert_errors


def save_tour(
    request: HttpRequest,
    tour: Tour,
    form: TourEditForm | TourForm,
    post_data: dict,
) -> Tour:
    """Save or create tour from recieved data.

    Args:
        request: HttpRequest - request from user.
        tour: Tour - tour for save.
        form: TourEditForm | TourForm - form for save data.
        post_data: dict - request post data for save.

    Returns:
        Tour: saved or created tour.
    """
    if tour:
        tour = form.save(commit=False)
        if post_data.get('avatar_clear') == 'on':
            tour.avatar.delete()
        if 'avatar' in request.FILES and post_data.get('avatar_clear') != 'on':
            tour.avatar = request.FILES['avatar']
        tour.save()
    else:
        tour = Tour.objects.create(**form.cleaned_data)
    return tour


def render_tour_form(
    request: HttpRequest,
    agency: Agency,
    form_data: dict,
    literals: dict,
    tour: Tour = None,
) -> str:
    """Pretty render tour form.

    Args:
        request: HttpRequest - request from user.
        agency: Agency - tour agency.
        form_data: dict - data for init form.
        literals: dict - literals for past into forms template.
        tour: Tour, optional - tour for render form. Defaults to None.

    Returns:
        str: rendered form.
    """
    errors = {}
    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['agency'] = str(agency.id)
        if tour:
            form = TourEditForm(instance=tour, data=post_data)
        else:
            form = TourForm(data=post_data, instance=tour)
        if form.is_valid():
            tour = save_tour(request, tour, form, post_data)
            addresses = form.cleaned_data.pop('addresses')
            tour.addresses.set(addresses)
            return redirect('tour', uuid=tour.id)
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    else:
        form = TourForm(**form_data)
    return render_to_string(
        'parts/tour_form.html',
        {
            'request': request,
            'form': form,
            'errors': errors,
            'title': literals.get('title'),
            'button': literals.get('button'),
            'button_name': literals.get('button_name'),
            'style_files': [
                'css/account_form.css',
                'css/tour_form.css',
            ],
        },
        request=request,
    )
