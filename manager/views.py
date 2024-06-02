"""Module with page views."""

from typing import Any

from django.contrib import auth
from django.contrib.auth import decorators
from django.db.models import Model
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render

from django.template.loader import render_to_string

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, permissions, viewsets
from rest_framework.serializers import ModelSerializer

from .forms import FindAgenciesForm, FindToursForm, SigninForm, SignupForm, SettingsUserForm, SettingsAgencyForm, SettingsAddressForm, PasswordChangeRequestForm, TourForm
from .models import Account, Address, Agency, Review, Tour
from .serializers import (AddressSerializer, AgencySerializer,
                          ReviewSerializer, TourSerializer)

from django.contrib.auth import views as auth_views

from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.html import strip_tags

from dotenv import load_dotenv
from os import getenv

from django.views.generic.base import View

from uuid import UUID

from .views_utils import render_reviews, convert_errors, render_tour_form


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
    reviews_data = {}
    for tour_data in tours_data:
        reviews_data[tour_data] = Review.objects.filter(tour=tour_data, account__agency=None)
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
                'css/rating.css',
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
                'css/rating.css',
            ],
        },
    )


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
    reviews_data = []
    if username:
        user = auth.models.User.objects.get(username=username)
        profile = Account.objects.filter(account=user).first()
    else:
        if not request.user.is_authenticated:
                return redirect('manager-login')
        profile = Account.objects.filter(account=request.user).first()
    if profile.agency:
        tours_data = Tour.objects.filter(agency=profile.agency.id)
        reviews_data = {tour_data: Review.objects.filter(tour=tour_data) for tour_data in tours_data}
        for tour_data, tour_reviews in reviews_data.items():
            tour_ratings = [review.rating for review in tour_reviews]
            if tour_ratings:
                reviews_data[tour_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
            else:
                reviews_data[tour_data] = 0
    else:
        reviews_data = list(Review.objects.filter(account=profile))
        reviews_data = render_reviews(
            request, reviews_data,
            display=True,
            check_user_review=False,
            link_to_tour=True,
        )
        if isinstance(reviews_data, HttpResponseRedirect):
            return reviews_data
    return render(
        request,
        'pages/profile.html',
        {
            'request_user': request.user,
            'user': profile,
            'tours_data': tours_data,
            'reviews_data': reviews_data,
            'review_form': '',
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/tours.css',
                'css/profile.css',
                'css/rating.css',
            ],
        },
    )


def settings(request: HttpRequest) -> HttpResponse:
    errors = {}
    request_user = request.user
    if not request_user.is_authenticated:
        return redirect('manager-login')
    user = Account.objects.filter(account=request_user).first()
    user_form = SettingsUserForm(request)
    agency_form, address_form = None, None
    if user.agency:
        agency_form = SettingsAgencyForm(request)
        address_form = SettingsAddressForm(request)
    if request.method == 'POST':
        post_request = request.POST
        if 'agency_submit' in post_request:
            agency_form = SettingsAgencyForm(data=post_request, instance=user.agency)
            address_form = SettingsAddressForm(data=post_request, instance=user.agency.address)
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
            else:
                address_errors = address_form.errors.as_data()
                agency_errors = agency_form.errors.as_data()
                address_errors = convert_errors(address_errors)
                agency_errors = convert_errors(agency_errors)
                errors.update(address_errors)
                errors.update(agency_errors)
        if 'user_submit' in post_request:
            user_form = SettingsUserForm(data=post_request, instance=request_user)
            if user_form.is_valid():
                user_form.save()
            else:
                user_errors = user_form.errors.as_data()
                user_errors = convert_errors(user_errors)
                errors.update(user_errors)
    return render(
        request,
        'pages/settings.html',
        {
            'request_user': request_user,
            'user': user,
            'user_form': user_form,
            'agency_form': agency_form,
            'address_form': address_form,
            'errors': errors,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/account_form.css',
                'css/profile.css',
                'css/settings.css',
                'css/rating.css',
            ],
        },
    )


@decorators.login_required
def request_password_change(request: HttpRequest) -> HttpResponse:
    errors = {}
    if request.method == 'POST':
        form = PasswordChangeRequestForm(request.POST)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            current_site = get_current_site(request)
            mail_subject = 'Confirm your password change'
            load_dotenv()
            html_message = render_to_string(
                'registration/password_change_email.html',
                {
                    'protocol': getenv('SITE_PROTOCOL'),
                    'user': user,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                },
            )
            plain_message = strip_tags(html_message)
            send_mail(
                mail_subject,
                plain_message,
                'zientenin@mail.ru',
                [user.email],
                html_message=html_message
            )
            request.session['new_password'] = new_password
            return redirect('password_change_done')
        else:
            errors = form.errors.as_data()
            errors = convert_errors(errors)
    else:
        form = PasswordChangeRequestForm()
    return render(
        request,
        'registration/password_change_form.html',
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


def confirm_password_change(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.filter(pk=uid).first()
    if user is not None and default_token_generator.check_token(user, token):
        new_password = request.session.get('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
            del request.session['new_password']
            return redirect('password_change_complete')
    return render(
        request,
        'registration/password_change_invalid.html',
        {
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/account_form.css',
            ],
        }
    )


def create_tour(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    account = Account.objects.filter(account=request.user).first()
    if not account.agency:
        raise PermissionDenied()
    agency = account.agency
    form_data = {'initial_data': {'agency': str(agency.id)}}
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
        raise PermissionDenied()
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


@decorators.login_required
def my_profile(request: HttpRequest) -> HttpResponse:
    return profile(request)


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
    reviews = render_reviews(request, reviews)
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
            ],
        }
    )


def create_stylized_auth_view(style_files: list | tuple) -> View:
    def class_decorator(original_class: object) -> View:
        class CustomView(original_class):
            def get_context_data(self, **kwargs):
                errors = {}
                context = super().get_context_data(**kwargs)
                form = context.get('form')
                if form:
                    errors = form.errors.as_data()
                    errors = convert_errors(errors)
                context['errors'] = errors
                context['style_files'] = style_files
                return context
        return CustomView
    return class_decorator


account_form_styles = [
    'css/header.css',
    'css/body.css',
    'css/account_form.css',
]

@create_stylized_auth_view(account_form_styles)
class CustomPasswordResetView(auth_views.PasswordResetView):
    html_email_template_name='registration/password_reset_email_html.html'

@create_stylized_auth_view(account_form_styles)
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    pass

@create_stylized_auth_view(account_form_styles)
class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    pass

@create_stylized_auth_view(account_form_styles)
class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    pass

@create_stylized_auth_view(account_form_styles)
class CustomPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name='registration/password_change_done.html'


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
