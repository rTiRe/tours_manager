"""Module with views for password change."""

import uuid

from django.contrib.auth import decorators, models, tokens, views
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils import encoding, http
from dotenv import load_dotenv

from ..profile_forms import PasswordChangeRequestForm
from ..views_utils import email_utils, errors_utils, profile_utils


@decorators.login_required
def request_password_change(request: HttpRequest) -> HttpResponse | HttpResponseRedirect:
    """View for request password change.

    Args:
        request: HttpRequest - request from user.

    Returns:
        HttpResponse: rendered page.
        HttpResponseRedirect: redirect to password change done page.
    """
    errors = {}
    if request.method == 'POST':
        form = PasswordChangeRequestForm(request.POST)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            mail_subject = 'Confirm your password change'
            load_dotenv()
            html_message = render_to_string(
                'registration/password_change_email.html',
                {
                    'managerprotocol': 'https' if request.is_secure() else 'http',
                    'user': user,
                    'domain': get_current_site(request).domain,
                    'uid': http.urlsafe_base64_encode(encoding.force_bytes(user.pk)),
                    'token': tokens.default_token_generator.make_token(user),
                },
            )
            email_utils.send_email(mail_subject, html_message, [user.email])
            request.session['new_password'] = new_password
            return redirect('password_change_done')
        else:
            errors = form.errors.as_data()
            errors = errors_utils.convert_errors(errors)
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
        },
    )


def confirm_password_change(
    request: HttpRequest,
    uidb64: uuid,
    token: str,
) -> HttpResponse | HttpResponseRedirect:
    """View for confirmation password change.

    Args:
        request: HttpRequest - request from user.
        uidb64: uuid - password change uid.
        token: str - password change token.

    Returns:
        HttpResponse: rendered page.
        HttpResponseRedirect: redirect to password change complete page.
    """
    uid = encoding.force_str(http.urlsafe_base64_decode(uidb64))
    user = models.User.objects.filter(pk=uid).first()
    if user is not None and tokens.default_token_generator.check_token(user, token):
        new_password = request.session.pop('new_password')
        if new_password:
            user.set_password(new_password)
            user.save()
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
        },
    )


account_form_styles = [
    'css/header.css',
    'css/body.css',
    'css/account_form.css',
]


@profile_utils.create_stylized_auth_view(account_form_styles)
class CustomPasswordResetView(views.PasswordResetView):
    """View for password reset."""

    html_email_template_name = 'registration/password_reset_email_html.html'


@profile_utils.create_stylized_auth_view(account_form_styles)
class CustomPasswordResetConfirmView(views.PasswordResetConfirmView):
    """View for password reset confirmation."""


@profile_utils.create_stylized_auth_view(account_form_styles)
class CustomPasswordResetDoneView(views.PasswordResetDoneView):
    """View for password reset done."""


@profile_utils.create_stylized_auth_view(account_form_styles)
class CustomPasswordResetCompleteView(views.PasswordResetCompleteView):
    """View for password reset complete."""


@profile_utils.create_stylized_auth_view(account_form_styles)
class CustomPasswordChangeDoneView(views.PasswordChangeDoneView):
    """View for password change done."""

    template_name = 'registration/password_change_done.html'
