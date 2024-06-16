"""Module with manager for render tours list."""

from os import getenv

from django.core.paginator import Paginator
from django.db.models import Manager
from django.http import HttpRequest
from django.template.loader import render_to_string
from dotenv import load_dotenv

from ..models import Review, Tour
from .page_utils import get_pages_slice

load_dotenv()
DEFAULT_TOURS_PER_PAGE = 15


class ToursListManager:
    """Manager for work with render tours list."""

    def __init__(
        self,
        request: HttpRequest,
        tours: list[Tour] | tuple[Tour],
        reviews: dict[Tour, Manager[Review]],
    ) -> None:
        """Init method.

        Args:
            request: HttpRequest - request from user.
            tours: list[Tour] | tuple[Tour] - tours for work.
            reviews: dict[Tour, Manager[Review]] - dict with tour object and list of his reviews.
        """
        self.request = request
        self.tours = tours
        self.reviews = reviews
        self.paginator = Paginator(tours, getenv('TOURS_PER_PAGE', DEFAULT_TOURS_PER_PAGE))

    def render_tour_card(self, tour: Tour, rating: float) -> str:
        """Render tour card view.

        Args:
            tour: Tour - tour for render.
            rating: float - rating of tour.

        Returns:
            str: rendered card.
        """
        return render_to_string(
            'parts/tour_card.html',
            {
                'tour_data': tour,
                'tour_rating': rating,
            },
            request=self.request,
        )

    def render_tours_list(self, page: int) -> str:
        """Render list of tours.

        Args:
            page: int - page of tours for render.

        Returns:
            str: rendered list.
        """
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
        """Render block with tours list.

        Returns:
            str: rendered block.
        """
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
