"""Module with page views."""

from typing import Any

from django.contrib.auth import authenticate, decorators, login, logout, models
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, permissions, viewsets
from rest_framework.serializers import ModelSerializer

from .forms import FindAgenciesForm, FindToursForm, SigninForm, SignupForm
from .models import Account, Address, Agency, Review, Tour
from .serializers import (AddressSerializer, AgencySerializer,
                          ReviewSerializer, TourSerializer)


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
    tours_data = Tour.objects.filter(
        starting_city=request.GET.get('starting_city'),
        address__city__country=request.GET.get('country'),
    )
    if not request.GET:
        tours_data = Tour.objects.all()
    reviews_data = {tour_data: Review.objects.filter(tour=tour_data) for tour_data in tours_data}
    for tour_data, tour_reviews in reviews_data.items():
        tour_ratings = [review.rating for review in tour_reviews]
        if tour_ratings:
            reviews_data[tour_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
        else:
            reviews_data[tour_data] = 0

    form = FindToursForm(request)
    return render(
        request,
        'pages/tours.html',
        {
            'form': form,
            'tours_data': tours_data,
            'tours_ratings': reviews_data,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tours.css',
                'css/search_tours.css',
            ],
        },
    )


def agencies(request: HttpRequest) -> HttpResponse:
    GET_city = request.GET.get('city')
    if not GET_city:
        agencies_data = Agency.objects.all()
    elif not request.GET:
        agencies_data = Agency.objects.all()
    else:
        agencies_data = Agency.objects.filter(address__city=GET_city)
    reviews_data = {agency_data: Review.objects.filter(tour__agency=agency_data) for agency_data in agencies_data}
    for agency_data, agency_reviews in reviews_data.items():
        tour_ratings = [review.rating for review in agency_reviews]
        if tour_ratings:
            reviews_data[agency_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
        else:
            reviews_data[agency_data] = 0
    form = FindAgenciesForm(request)
    return render(
        request,
        'pages/agencies.html',
        {
            'form': form,
            'agencies_data': agencies_data,
            'reviews_data': reviews_data,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/agencies.css',
                'css/search_agencies.css',
            ],
        },
    )


def convert_errors(errors: dict) -> dict:
    readable_dict = {}
    for field_name, field_errors in errors.items():
        for error in field_errors:
            error = str(error)
            if error.startswith('[\'') and error.endswith('\']'):
                error = error[2:-2]
                readable_dict[field_name] = error
    return readable_dict


def signup(request):
    errors = {}
    if request.user.is_authenticated:
        return redirect('my_profile')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(account=user)
            login(request, user)
            return redirect('signin')
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    else:
        form = SignupForm()
    return render(
        request,
        'signup/signup.html',
        {
            'form': form,
            'errors': errors,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/account_form.css',
            ],
        }
    )


def signin(request):
    errors = {}
    if request.user.is_authenticated:
        return redirect('my_profile')
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user) 
                return redirect('my_profile')
            else:
                errors['username'] = _('The username or password seems to be incorrect.')
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    else:
        form = SigninForm()
    print(errors)
    return render(
        request,
        'signup/signin.html',
        {
            'form': form,
            'errors': errors,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/account_form.css',
            ],
        }
    )


def signout(request):
    logout(request)
    return redirect('signin')


def profile(request: HttpRequest, username: str = None) -> HttpResponse:
    tours_data = {}
    reviews_data = {}
    if username:
        user_id = models.User.objects.get(username=username).id
        profile = Account.objects.get(account=user_id)
    else:
        if not request.user.is_authenticated:
                return redirect('signin')
        profile = Account.objects.get(account=request.user)
    if profile.agency:
        tours_data = Tour.objects.filter(agency=profile.agency.id)
        reviews_data = {tour_data: Review.objects.filter(tour=tour_data) for tour_data in tours_data}
        for tour_data, tour_reviews in reviews_data.items():
            tour_ratings = [review.rating for review in tour_reviews]
            if tour_ratings:
                reviews_data[tour_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
            else:
                reviews_data[tour_data] = 0
    return render(
        request,
        'pages/profile.html',
        {
            'request_user': request.user,
            'user': profile,
            'tours_data': tours_data,
            'reviews_data': reviews_data,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tours.css',
                'css/profile.css',
            ],
        },
    )


def csrf_failure(request, reason=""):
    return redirect('index')


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
