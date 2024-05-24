"""Module with page views."""

from typing import Any

from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from rest_framework import authentication, permissions, viewsets
from rest_framework.serializers import ModelSerializer

from .models import Address, Agency, Review, Tour, Account
from .serializers import (AddressSerializer, AgencySerializer,
                          ReviewSerializer, TourSerializer)
from .forms import FindToursForm, SignupForm, SigninForm

from uuid import UUID

from django.contrib.auth import decorators


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
                'css/index.css',
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
        'tours.html',
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


def signup(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(account=user)
            login(request, user)
            return redirect('profile')
    else:
        form = SignupForm()
    return render(request, 'signup/signup.html', {'signup_form': form})


def signin(request):
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user) 
                return redirect('/profile/')
    else:
        form = SigninForm()
    return render(request, 'signup/signin.html', {'signin_form': form})


def signout(request):
    logout(request)
    return redirect('signin')


def profile(request: HttpRequest, pk: UUID = None) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect('signin')
    if pk:
        client = Account.objects.get(id=pk)
    else:
        client = Account.objects.get(account=request.user)
    return render(
        request,
        'pages/profile.html',
        {
            'user': client,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tours.css',
                'css/search_tours.css',
            ],
        },
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
