"""Module with page views."""

from os import getenv
from uuid import UUID

from django.core import exceptions, paginator
from django.http import (HttpRequest, HttpResponse, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.urls import reverse
from dotenv import load_dotenv

from .forms import FindAgenciesForm, FindToursForm
from .models import Account, Agency, Review, Tour
from .views_utils import page_utils, render_tour_form, reviews_list_manager, tours_list_manager, address_form_utils
from django.utils.translation import gettext_lazy as _
load_dotenv()


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
            'form': form,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/search_tours.css',
            ],
        },
    )


def tours(request: HttpRequest) -> HttpResponse:
    if not request.GET or not set(('starting_city', 'country')).issubset(request.GET):
        tours_data = Tour.objects.all()
    else:
        tours_data = Tour.objects.filter(
            starting_city=request.GET.get('starting_city'),
            address__city__country=request.GET.get('country'),
        )
    print(tours_data)
    reviews_data = {}
    for tour_data in tours_data:
        reviews_data[tour_data] = Review.objects.filter(tour=tour_data, account__agency=None)
    tours_manager = tours_list_manager.ToursListManager(request, tours_data, reviews_data)
    print(tours_manager.paginator)
    tours_block = tours_manager.render_tours_block()
    form = FindToursForm(request)
    return render(
        request,
        'pages/tours.html',
        {
            'form': form,
            'tours_block': tours_block,
            'reviews_data': reviews_data,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/search_tours.css',
                'css/rating.css',
                'css/avatar.css',
            ],
        },
    )


def agencies(request: HttpRequest) -> HttpResponse:
    get_city = request.GET.get('city')
    page = int(request.GET.get('page', 1))
    if not request.GET or not get_city:
        agencies_data = Agency.objects.all()
    else:
        agencies_data = Agency.objects.filter(address__city=get_city)
    agencies_data = [agency for agency in agencies_data if hasattr(agency, 'account')]
    agencies_paginator = paginator.Paginator(agencies_data, int(getenv('AGENCIES_PER_PAGE', 15)))
    agencies_data = agencies_paginator.get_page(page)
    reviews_data = {agency: Review.objects.filter(tour__agency=agency) for agency in agencies_data}
    for agency_data, agency_reviews in reviews_data.items():
        tour_ratings = [review.rating for review in agency_reviews]
        if tour_ratings:
            reviews_data[agency_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
        else:
            reviews_data[agency_data] = 0
    num_pages = int(agencies_paginator.num_pages)
    pages_slice = page_utils.get_pages_slice(page, num_pages)
    form = FindAgenciesForm(request)
    return render(
        request,
        'pages/agencies.html',
        {
            'form': form,
            'agencies_data': agencies_data,
            'reviews_data': reviews_data,
            'pages': {
                'current': page,
                'total': num_pages,
                'slice': pages_slice,
            },
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/agencies.css',
                'css/search_agencies.css',
                'css/rating.css',
                'css/avatar.css',
                'css/pages.css',
            ],
        },
    )


def create_tour(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    account = Account.objects.filter(account=request.user).first()
    if not account.agency:
        raise exceptions.PermissionDenied()
    agency = account.agency
    form_data = {'initial': {'agency': str(agency.id)}}
    form = render_tour_form(
        request,
        agency=agency,
        form_data=form_data,
        literals={
            'title': 'Создание тура',
            'button': 'Создать',
            'bitton_name': 'create',
        }
    )
    return render(
        request,
        'pages/create_tour.html',
        {
            'form': form,
            'style_files': [
                'css/header.css',
                'css/body.css',
            ],
        }
    )


def delete_tour(request: HttpRequest, uuid: UUID) -> HttpResponse:
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
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/account_form.css',
            ],
        }
    )


def edit_tour(request: HttpRequest, uuid: UUID) -> HttpResponse:
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
    form = render_tour_form(
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
            'form': form,
            'style_files': [
                'css/header.css',
                'css/body.css',
            ],
        }
    )


def csrf_failure(request: HttpRequest, reason: str = '') -> HttpResponseRedirect:
    return redirect('index')


def tour(request: HttpRequest, uuid: UUID) -> HttpResponse:
    ratings = []
    tour_data = Tour.objects.filter(id=uuid).first()
    if not tour_data:
        return HttpResponseNotFound()
    reviews = list(tour_data.reviews.filter(account__agency=None))
    for review in reviews:
        ratings.append(review.rating)
    reviews = reviews_list_manager.ReviewsListManager(request, reviews, reverse('tour', kwargs={'uuid': uuid}))
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
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tour.css',
                'css/rating.css',
                'css/avatar.css',
            ],
        }
    )


def create_address(request: HttpRequest) -> HttpResponse:
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
            'button': _('Create')
        },
    )
    if isinstance(form, HttpResponseRedirect):
        return form
    return render(
        request,
        'pages/create_address.html',
        {
            'form': form,
            'style_files': [
                'css/header.css',
                'css/body.css',
            ],
        }
    )


