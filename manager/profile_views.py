"""Module with views for user profile."""

from django.contrib.auth import decorators
from django.contrib.auth import models as auth_models
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import SettingsAddressForm, SettingsAgencyForm, SettingsUserForm
from .models import Account, Address, Review, Tour
from .views_utils import convert_errors, reviews_list_manager, tours_list_manager


def profile(request: HttpRequest, username: str = None) -> HttpResponse | HttpResponseRedirect:
    tours_data = {}
    reviews = {}
    if username:
        user = auth_models.User.objects.get(username=username)
        account = Account.objects.filter(account=user).first()
    else:
        if not request.user.is_authenticated:
            return redirect('manager-login')
        account = Account.objects.filter(account=request.user).first()
    if account.agency:
        tours_data = Tour.objects.filter(agency=account.agency.id)
        reviews_data = {tour: Review.objects.filter(tour=tour) for tour in tours_data}
        tours_manager = tours_list_manager.ToursListManager(request, tours_data, reviews_data)
        tours_block = tours_manager.render_tours_block()
        for tour_data, tour_reviews in reviews_data.items():
            tour_ratings = [review.rating for review in tour_reviews]
            if tour_ratings:
                reviews_data[tour_data] = round(sum(tour_ratings) / len(tour_ratings), 2)
            else:
                reviews_data[tour_data] = 0
    else:
        reviews_data = list(Review.objects.filter(account=account))
        reviews = reviews_list_manager.ReviewsListManager(
            request,
            reviews_data,
            reverse('my_profile'),
            'parts/tour_review.html',
        )
        reviews_data = reviews.render_reviews_block(display=True, check_user_review=False)
        if isinstance(reviews_data, HttpResponseRedirect):
            return reviews_data
    return render(
        request,
        'pages/profile.html',
        {
            'request_user': request.user,
            'user': account,
            'tours_block': tours_block,
            'reviews_data': reviews_data,
            'review_form': '',
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/profile.css',
                'css/rating.css',
                'css/avatar.css',
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
            user_form = SettingsUserForm(request, post_request, request.FILES, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                if post_request.get('avatar_clear') == 'on':
                    user.avatar.delete()
                    user.save()
                if 'avatar' in request.FILES and post_request.get('avatar_clear') != 'on':
                    user.avatar = request.FILES['avatar']
                    user.save()
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
            'ignore_special_header': True,
            'style_files': [
                'css/header.css',
                'css/body.css',
                'css/account_form.css',
                'css/profile.css',
                'css/settings.css',
                'css/rating.css',
                'css/avatar.css',
            ],
        },
    )


@decorators.login_required
def my_profile(request: HttpRequest) -> HttpResponse:
    """Render authenticated user profile.

    Args:
        request (HttpRequest): _description_

    Returns:
        HttpResponse: _description_
    """
    return profile(request)


@decorators.login_required
def get_api_token(request: HttpRequest) -> HttpResponse:
    pass