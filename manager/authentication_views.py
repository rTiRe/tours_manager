"""Module with authentication views."""

from django.contrib.auth import authenticate, decorators
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from .forms import SigninForm, SignupForm
from .models import Account
from .views_utils import convert_errors
from .views_utils.email_utils import send_email


def registration(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """User registration view.

    Args:
        request: HttpRequest - request from user.

    Returns:
        HttpResponse: rendered registration page.
        HttpResponseRedirect: redirect to login page.
    """
    errors = {}
    if request.user.is_authenticated:
        return redirect('my_profile')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            created_account = Account.objects.create(account=user)
            token = Token.objects.create(user=created_account.account)
            mail_subject = 'Welcome! Thats your API auth key!'
            html_message = render_to_string(
                'registration/token_email.html',
                {'api_key': token.key},
            )
            send_email(mail_subject, html_message, [user.email])
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
        },
    )


def login(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """User login view.

    Args:
        request: HttpRequest - request from user.

    Returns:
        HttpResponse: rendered login page.
        HttpResponseRedirect: redirect to user profile.
    """
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
                auth_login(request, user)
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
        },
    )


@decorators.login_required
def logout(request: HttpRequest) -> HttpResponseRedirect:
    """User logout view.

    Args:
        request: HttpRequest - request from user.

    Returns:
        HttpResponseRedirect: redirect to login page.
    """
    auth_logout(request)
    return redirect('manager-login')
