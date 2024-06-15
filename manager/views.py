"""Module with page views."""

from typing import Any
from uuid import UUID

from django.core import exceptions, paginator
from django.db.models import Model
from django.http import (HttpRequest, HttpResponse, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import redirect, render
from django.urls import reverse
from rest_framework import authentication, permissions, viewsets
from rest_framework.serializers import ModelSerializer

from .forms import FindAgenciesForm, FindToursForm
from .models import Account, Address, Agency, Review, Tour
from .serializers import (AddressSerializer, AgencySerializer,
                          ReviewSerializer, TourSerializer)
from .views_utils import render_tour_form, reviews_manager, page_utils
from dotenv import load_dotenv
from os import getenv

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
    page = int(request.GET.get('page', 1))
    if not request.GET:
        tours_data = Tour.objects.all()
    else:
        tours_data = Tour.objects.filter(
            starting_city=request.GET.get('starting_city'),
            address__city__country=request.GET.get('country'),
        )
    tours_paginator = paginator.Paginator(tours_data, int(getenv('TOURS_PER_PAGE', 15)))
    tours_data = tours_paginator.get_page(page)
    reviews_data = {}
    for tour_data in tours_data:
        reviews_data[tour_data] = Review.objects.filter(tour=tour_data, account__agency=None)
    for tour_data, tour_reviews in reviews_data.items():
        tour_ratings = [review.rating for review in tour_reviews]
        if tour_ratings:
            reviews_data[tour_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
        else:
            reviews_data[tour_data] = 0
    num_pages = int(tours_paginator.num_pages)
    pages_slice = page_utils.get_pages_slice(page, num_pages)
    form = FindToursForm(request)
    return render(
        request,
        'pages/tours.html',
        {
            'form': form,
            'tours_data': tours_data,
            'reviews_data': reviews_data,
            'pages': {
                'current': page,
                'total': num_pages,
                'slice': pages_slice,
            },
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tours.css',
                'css/search_tours.css',
                'css/rating.css',
                'css/avatar.css',
                'css/pages.css',
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
    tour = Tour.objects.filter(id=uuid).first()
    if not tour:
        return HttpResponseNotFound()
    reviews = list(tour.reviews.filter(account__agency=None))
    for review in reviews:
        ratings.append(review.rating)
    reviews = reviews_manager(request, reviews, reverse('tour', kwargs={'uuid': uuid}))
    reviews = reviews.render_reviews_block()
    if isinstance(reviews, HttpResponseRedirect):
        return reviews
    return render(
        request,
        'pages/tour.html',
        {
            'ratings': ratings,
            'reviews': reviews,
            'tour': tour,
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


class CustomViewSetPermission(permissions.BasePermission):
    """Custom permission for viewset."""

    _safe_methods = 'GET', 'HEAD', 'OPTIONS', 'TRACE'
    _unsafe_methods = 'PATCH', 'POST', 'PUT', 'DELETE'

    def has_permission(self, request: HttpRequest, _: Any) -> bool:
        """Check user permissions.

        Args:
            request: HttpRequest - request from user.
            _: Any - other data.

        Returns:
            bool: True if user has required permissions.
        """
        user = request.user
        if request.method in self._safe_methods and (user and user.is_authenticated):
            return True
        return request.method in self._unsafe_methods and (user and user.is_superuser)


def create_viewset(model_class: Model, serializer: ModelSerializer) -> viewsets.ModelViewSet:
    """Viewset decorator.

    Args:
        model_class: Model - model for generate viewset.
        serializer: ModelSerializer - serializer for model.

    Returns:
        ModelViewSet: model viewset.
    """
    class CustomViewSet(viewsets.ModelViewSet):
        serializer_class = serializer
        queryset = model_class.objects.all()
        permission_classes = [CustomViewSetPermission]
        authentication_classes = [authentication.TokenAuthentication]
    return CustomViewSet


AgencyViewSet = create_viewset(Agency, AgencySerializer)
TourViewSet = create_viewset(Tour, TourSerializer)
AddressViewSet = create_viewset(Address, AddressSerializer)
ReviewViewSet = create_viewset(Review, ReviewSerializer)
