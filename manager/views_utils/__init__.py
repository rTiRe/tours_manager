from django.http import HttpRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from ..forms import TourEditForm, TourForm
from ..models import Agency, Tour


def convert_errors(errors: dict) -> dict:
    readable_dict = {}
    for field_name, field_errors in errors.items():
        for error in field_errors:
            error = str(error)
            if error.startswith("['") and error.endswith("']"):
                error = error[2:-2]
                readable_dict[field_name] = error
    return readable_dict

def render_tour_form(
        request: HttpRequest,
        agency: Agency,
        form_data: dict,
        literals: dict,
        tour: Tour = None,
    ) -> str:
        errors = {}
        if request.method == 'POST':
            post_data = request.POST.copy()
            post_data['agency'] = str(agency.id)
            if tour:
                form = TourEditForm(instance=tour, data=post_data)
            else:
                form = TourForm(data=post_data, instance=tour)
            if form.is_valid():
                if not tour:
                    tour = Tour.objects.create(**form.cleaned_data)
                else:
                    tour = form.save(commit=False)
                    if post_data.get('avatar_clear') == 'on':
                        tour.avatar.delete()
                    if 'avatar' in request.FILES and post_data.get('avatar_clear') != 'on':
                        tour.avatar = request.FILES['avatar']
                    tour.save()
                addresses = form.cleaned_data.pop('addresses')
                tour.addresses.set(addresses)
                return redirect('tour', uuid=tour.id)
            else:
                errors = form.errors.as_data()
                errors = convert_errors(errors)
        else:
            form = TourForm(**form_data)
        return render_to_string(
            'parts/tour_form.html',
            {
                'request': request,
                'form': form,
                'errors': errors,
                'title': literals.get('title'),
                'button': literals.get('button'),
                'button_name': literals.get('button_name'),
                'style_files': [
                    'css/account_form.css',
                    'css/tour_form.css',
                ],
            },
            request=request,
        )
