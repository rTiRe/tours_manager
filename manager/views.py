"""Module with page views."""

from typing import Any

from django.contrib import auth
from django.contrib.auth import decorators
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, permissions, viewsets
from rest_framework.serializers import ModelSerializer

from .forms import FindAgenciesForm, FindToursForm, SigninForm, SignupForm, SettingsUserForm, SettingsAgencyForm, SettingsAddressForm
from .models import Account, Address, Agency, Review, Tour
from .serializers import (AddressSerializer, AgencySerializer,
                          ReviewSerializer, TourSerializer)

from django.contrib.auth import views as auth_views

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from .forms import PasswordChangeRequestForm
from django.views.generic import TemplateView


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


def registration(request):
    errors = {}
    if request.user.is_authenticated:
        return redirect('my_profile')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(account=user)
            return redirect('manager-login')
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    else:
        form = SignupForm()
    return render(
        request,
        'registration/registration.html',
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


def login(request):
    errors = {}
    if request.user.is_authenticated:
        return redirect('my_profile')
    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(request, username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect('my_profile')
            else:
                errors['username'] = _('The username or password seems to be incorrect.')
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    else:
        form = SigninForm()
    return render(
        request,
        'registration/login.html',
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


def logout(request):
    auth.logout(request)
    return redirect('manager-login')


def profile(request: HttpRequest, username: str = None) -> HttpResponse:
    tours_data = {}
    reviews_data = {}
    if username:
        user_id = auth.models.User.objects.get(username=username).id
        profile = Account.objects.get(account=user_id)
    else:
        if not request.user.is_authenticated:
                return redirect('manager-login')
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


def settings(request: HttpRequest) -> HttpResponse:
    request_user = request.user
    if not request_user.is_authenticated:
        return redirect('manager-login')
    user = Account.objects.get(account=request_user.id)
    user_form = SettingsUserForm(request)
    agency_form = SettingsAgencyForm(request)
    address_form = SettingsAddressForm(request)
    if request.method == 'POST':
        post_request = request.POST
        if 'agency_submit' in post_request:
            agency_form = SettingsAgencyForm(data=post_request, instance=user.agency)
            address_form = SettingsAddressForm(data=post_request)
            if agency_form.is_valid() and address_form.is_valid():
                cleaned_data = address_form.cleaned_data
                cleaned_data = {
                    'city': cleaned_data['city'],
                    'street': cleaned_data['street'],
                    'house_number': cleaned_data['house_number'],
                    'entrance_number': cleaned_data['entrance_number'],
                    'floor': cleaned_data['floor'],
                    'flat_number': cleaned_data['flat_number'],
                    'point': cleaned_data['point'],
                }
                existing_address = Address.objects.filter(**cleaned_data).first()
                if existing_address:
                    user.agency.address = existing_address
                else:
                    new_address = Address.objects.create(**cleaned_data)
                    user.agency.address = new_address
                agency_form.save()
        if 'user_submit' in post_request:
            user_form = SettingsUserForm(data=post_request, instance=request_user)
            if user_form.is_valid():
                user_form.save()
            else:
                print(user_form.errors)
    return render(
        request,
        'pages/settings.html',
        {
            'request_user': request_user,
            'user': user,
            'user_form': user_form,
            'agency_form': agency_form,
            'address_form': address_form,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tours.css',
                'css/profile.css',
            ],
        },
    )


@decorators.login_required
def request_password_change(request):
    if request.method == 'POST':
        form = PasswordChangeRequestForm(request.POST)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            mail_subject = 'Confirm your password change'
            message = render_to_string('registration/password_change_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            })
            send_mail(mail_subject, message, 'zientenin@mail.ru', [user.email])
            request.session['new_password'] = new_password
            return redirect('password_change_done')
    else:
        form = PasswordChangeRequestForm()
    return render(request, 'registration/password_change_form.html', {'form': form})


def confirm_password_change(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Получите новый пароль из сессии
        new_password = request.session.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            # Удалите новый пароль из сессии
            del request.session['new_password']
            return redirect('password_change_complete')
        else:
            return render(request, 'registration/password_change_invalid.html')
    else:
        return render(request, 'registration/password_change_invalid.html')

class PasswordChangeCompleteView(TemplateView):
    template_name = 'registration/password_change_complete.html'


@decorators.login_required
def my_profile(request: HttpRequest) -> HttpResponse:
    return profile(request)


def csrf_failure(request, reason=""):
    return redirect('index')


class PasswordChangeCompleteView(TemplateView):
    template_name = 'registration/password_change_complete.html'


class CustomPasswordResetView(auth_views.PasswordResetView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['my_variable'] = 'My custom value'
        context['another_variable'] = 'Another value'
        return context


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
