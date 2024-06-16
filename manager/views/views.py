"""Module with page views."""

from os import getenv
from uuid import UUID

from django.core import exceptions, paginator
from django.http import (HttpRequest, HttpResponse, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from ..forms import FindAgenciesForm, FindToursForm
from ..models import Account, Agency, Review, Tour
from ..views_utils import (address_form_utils, page_utils,
                           reviews_list_manager, tour_utils,
                           tours_list_manager)

load_dotenv()
DEFAULT_AGECIES_PER_PAGE = 15
FORM_LITERAL = 'form'
STYLE_FILES_LITERAL = 'style_files'
HEADER_CSS = 'css/header.css'
BODY_CSS = 'css/body.css'


def index(request: HttpRequest) -> HttpResponse:
    """Index page view.

    Args:
        request: HttpRequest - request from user..

    Returns:
        HttpResponse: response from server.
    """
    form = FindToursForm()
    return render(
        request,
        'index.html',
        {
            FORM_LITERAL: form,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
                'css/search_tours.css',
            ],
        },
    )


def tours(request: HttpRequest) -> HttpResponse:
    """Tours list view.

    Args:
        request: HttpRequest - request from user.

    Returns:
        HttpResponse: rendered template.
    """
    expected_get_subset = ['starting_city', 'country']
    if not request.GET or not set(expected_get_subset).issubset(request.GET):
        tours_data = Tour.objects.all()
    else:
        tours_data = Tour.objects.filter(
            starting_city=request.GET.get('starting_city'),
            address__city__country=request.GET.get('country'),
        )
    reviews_data = {}
    for tour_data in tours_data:
        reviews_data[tour_data] = Review.objects.filter(tour=tour_data, account__agency=None)
    tours_manager = tours_list_manager.ToursListManager(request, tours_data, reviews_data)
    tours_block = tours_manager.render_tours_block()
    form = FindToursForm(request)
    return render(
        request,
        'pages/tours.html',
        {
            FORM_LITERAL: form,
            'tours_block': tours_block,
            'reviews_data': reviews_data,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
                'css/search_tours.css',
                'css/rating.css',
                'css/avatar.css',
            ],
        },
    )


def agencies(request: HttpRequest) -> HttpResponse:
    """Viw with list of all agencies.

    Args:
        request: HttpRequest - request from user.

    Returns:
        HttpResponse: rendered template.
    """
    page = int(request.GET.get('page', 1))
    if not request.GET or not request.GET.get('city'):
        agencies_data = Agency.objects.all()
    else:
        agencies_data = Agency.objects.filter(address__city=request.GET.get('city'))
    agencies_data = [
        agency for agency in agencies_data if hasattr(agency, 'account')  # noqa: WPS421
    ]
    agencies_paginator = paginator.Paginator(
        agencies_data,
        int(getenv('AGENCIES_PER_PAGE', DEFAULT_AGECIES_PER_PAGE)),
    )
    agencies_data = agencies_paginator.get_page(page)
    reviews_data = {agency: Review.objects.filter(tour__agency=agency) for agency in agencies_data}
    for agency_data, agency_reviews in reviews_data.items():
        tour_ratings = [review.rating for review in agency_reviews]
        if tour_ratings:
            reviews_data[agency_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
        else:
            reviews_data[agency_data] = 0
    pages_slice = page_utils.get_pages_slice(page, int(agencies_paginator.num_pages))
    return render(
        request,
        'pages/agencies.html',
        {
            FORM_LITERAL: FindAgenciesForm(request),
            'agencies_data': agencies_data,
            'reviews_data': reviews_data,
            'pages': {
                'current': page,
                'total': int(agencies_paginator.num_pages),
                'slice': pages_slice,
            },
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
                'css/agencies.css',
                'css/search_agencies.css',
                'css/rating.css',
                'css/avatar.css',
                'css/pages.css',
            ],
        },
    )


def create_tour(request: HttpRequest) -> HttpResponse:
    """View for create tour form.

    Args:
        request: HttpRequest - request from user.

    Raises:
        PermissionDenied: if user dont have acess to this page.

    Returns:
        HttpResponse: rendered template.
    """
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    account = Account.objects.filter(account=request.user).first()
    if not account.agency:
        raise exceptions.PermissionDenied()
    agency = account.agency
    form_data = {'initial': {'agency': str(agency.id)}}
    form = tour_utils.render_tour_form(
        request,
        agency=agency,
        form_data=form_data,
        literals={
            'title': 'Создание тура',
            'button': 'Создать',
            'bitton_name': 'create',
        },
    )
    return render(
        request,
        'pages/create_tour.html',
        {
            FORM_LITERAL: form,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
            ],
        },
    )


def delete_tour(request: HttpRequest, uuid: UUID) -> HttpResponse:
    """View for delete tour form.

    Args:
        request: HttpRequest - request from user.
        uuid: UUID - tour id

    Raises:
        PermissionDenied: if user dont have permissions for this action.

    Returns:
        HttpResponse: rendered template.
    """
    tour = Tour.objects.filter(id=uuid).first()
    if not tour:
        return HttpResponseNotFound()
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    account = Account.objects.filter(account=request.user).first()
    if not account.agency:
        return HttpResponseNotFound()
    if tour.agency.account != account:
        raise exceptions.PermissionDenied()
    if request.method == 'POST':
        if 'delete' in request.POST:
            tour.delete()
        return redirect('my_profile')
    return render(
        request,
        'pages/delete_tour.html',
        {
            'tour': tour,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
                'css/account_form.css',
            ],
        },
    )


def edit_tour(request: HttpRequest, uuid: UUID) -> HttpResponse:
    """View for edit tour form.

    Args:
        request: HttpRequest - request from user.
        uuid: UUID - tour id.

    Raises:
        PermissionDenied: if user dont have permission to visit this page.

    Returns:
        HttpResponse: rendered template.
    """
    tour = Tour.objects.filter(id=uuid).first()
    if not tour:
        return HttpResponseNotFound()
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    account = Account.objects.filter(account=request.user).first()
    if not account.agency:
        return HttpResponseNotFound()
    if tour.agency.account != account:
        raise exceptions.PermissionDenied()
    agency = account.agency
    initial_data = {'addresses': [str(address.id) for address in tour.addresses.all()]}
    form_data = {'instance': tour, 'initial': initial_data}
    form = tour_utils.render_tour_form(
        request,
        agency=agency,
        form_data=form_data,
        literals={
            'title': 'Редактирование тура',
            'button': 'Сохранить',
            'button_name': 'edit',
        },
        tour=tour,
    )
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'pages/edit_tour.html',
        {
            FORM_LITERAL: form,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
            ],
        },
    )


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponseRedirect:
    """View for CSRF failure.

    Args:
        request: HttpRequest - request from user.
        reason: str, optional - failure reason. Defaults to ''.

    Returns:
        HttpResponseRedirect: redirect to page.
    """
    return redirect('index')


def tour(request: HttpRequest, uuid: UUID) -> HttpResponse:
    """Tour view.

    Args:
        request: HttpRequest - request from user.
        uuid: UUID - tour id.

    Returns:
        HttpResponse: rendered template.
    """
    ratings = []
    tour_data = Tour.objects.filter(id=uuid).first()
    if not tour_data:
        return HttpResponseNotFound()
    reviews = list(tour_data.reviews.filter(account__agency=None))
    for review in reviews:
        ratings.append(review.rating)
    reviews = reviews_list_manager.ReviewsListManager(
        request,
        reviews,
        reverse('tour', kwargs={'uuid': uuid}),
    )
    reviews = reviews.render_reviews_block()
    if isinstance(reviews, HttpResponseRedirect):
        return reviews
    return render(
        request,
        'pages/tour.html',
        {
            'ratings': ratings,
            'reviews': reviews,
            'tour': tour_data,
            'request': request,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
                'css/tour.css',
                'css/rating.css',
                'css/avatar.css',
            ],
        },
    )


def create_address(request: HttpRequest) -> HttpResponse:
    """View for create address form.

    Args:
        request: HttpRequest - request from user.

    Raises:
        PermissionDenied: if user dont have permissions for create address.

    Returns:
        HttpResponse: rendered template.
    """
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    account = Account.objects.filter(account=request.user).first()
    if not account.agency and not request.user.is_staff:
        raise exceptions.PermissionDenied()
    form = address_form_utils.render_address_form(
        request,
        {
            'title': _('Create address'),
            'button_name': 'create',
            'button': _('Create'),
        },
    )
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'pages/create_address.html',
        {
            FORM_LITERAL: form,
            STYLE_FILES_LITERAL: [
                HEADER_CSS,
                BODY_CSS,
            ],
        },
    )
