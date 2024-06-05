from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from ..forms import UserReviewForm, TourForm, TourEditForm
from ..models import Account, Review, Tour, Agency
from ..validators import get_datetime
from django.core.paginator import Paginator
# from . import convert_errors

class ToursManager:
    def __init__(
        self,
        request: HttpRequest,
        tours: list[Tour] | tuple[Tour],
        items_per_page: int = 5,
    ):
        pass