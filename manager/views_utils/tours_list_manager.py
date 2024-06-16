from os import getenv

from django.db.models import Manager
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

from ..models import Tour, Review
from .page_utils import get_pages_slice

load_dotenv()

class ToursListManager:
    def __init__(
        self,
        request: HttpRequest,
        tours: list[Tour] | tuple[Tour],
        reviews: dict[Tour, Manager[Review]],
        tour_template_name: str = 'parts/tour_card.html',
    ) -> None:
        self.request = request
        self.tours = tours
        self.tour_template_name = tour_template_name
        self.reviews = reviews
        self.paginator = Paginator(tours, getenv('TOURS_PER_PAGE', 15))

    def render_tour_card(self, tour: Tour, rating: float) -> str:
        return render_to_string(
            'parts/tour_card.html',
            {
                'tour_data': tour,
                'tour_rating': rating,
            },
            request=self.request,
        )

    def render_tours_list(self, page: int) -> str:
        rendered_tours = []
        tours_page = self.paginator.get_page(page)
        for tour in tours_page:
            tour_reviews = self.reviews[tour]
            tour_ratings = [review.rating for review in tour_reviews]
            if tour_ratings:
                tour_rating = round(sum(tour_ratings) / len(tour_ratings), 2)
            else:
                tour_rating = 0
            rendered_tour_card = self.render_tour_card(tour, tour_rating)
            rendered_tours.append(rendered_tour_card)
        return render_to_string(
            'parts/tours_list.html',
            {
                'tours': rendered_tours,
            },
            request=self.request,
        )

    def render_tours_block(self) -> str:
        page = int(self.request.GET.get('page', 1))
        tours_list = self.render_tours_list(page=page)
        num_pages = int(self.paginator.num_pages)
        pages_slice = get_pages_slice(page, num_pages)
        pages_slice = ''.join(pages_slice)
        return render_to_string(
            'parts/tours_block.html',
            {
                'request': self.request,
                'tours_list': tours_list,
                'pages': {
                    'current': page,
                    'total': num_pages,
                    'slice': pages_slice,
                },
                'style_files': [
                    'css/tours.css',
                    'css/pages.css',
                ],
            },
            request=self.request,
        )