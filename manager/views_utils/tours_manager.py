from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from ..forms import TourEditForm, TourForm, UserReviewForm
from ..models import Account, Agency, Review, Tour
from ..validators import get_datetime

# from . import convert_errors

class ToursManager:
    def __init__(
        self,
        request: HttpRequest,
        tours: list[Tour] | tuple[Tour],
        items_per_page: int = 5,
    ):
        pass