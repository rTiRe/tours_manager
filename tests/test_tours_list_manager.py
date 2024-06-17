from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.http import HttpRequest
from django.test import RequestFactory, TestCase

from manager.models import (Account, Address, Agency, City, Country, Review,
                            Tour)
from manager.views_utils.tours_list_manager import ToursListManager


class ToursListManagerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/fake-url')
        user = User.objects.create_user(username='tester', password='123')
        account = Account.objects.create(account=user)
        country = Country.objects.create(name="USA")
        city = City.objects.create(
            name="New York",
            country=country,
            point=Point(-74.0060, 40.7128)
        )
        agency_address = Address.objects.create(
            city=city,
            street="Liberty St",
            house_number="1700", 
            point=Point(-74.0061, 40.7129),
        )
        agency = Agency.objects.create(name="TravelFun", phone_number="+79999999999", address=agency_address)
        self.tours = [Tour.objects.create(name=f"Tour {i}", description="Sample", agency=agency, price=400, starting_city=city) for i in range(5)]
        self.reviews = {tour: [Review.objects.create(tour=tour, rating=5, account=account)] for tour in self.tours}
        self.manager = ToursListManager(self.request, self.tours, self.reviews)

    def test_initialization(self):
        self.assertIsInstance(self.manager, ToursListManager)
        self.assertEqual(len(self.manager.tours), 5)

    def test_render_tour_card(self):
        tour = self.tours[0]
        rating = 5
        result = self.manager.render_tour_card(tour, rating)
        self.assertIn(tour.name, result)
        self.assertNotIn('<span class="fa fa-star"></span>', result)

    def test_render_tours_list(self):
        result = self.manager.render_tours_list(1)
        self.assertIn('Tour 0', result)
        self.assertIn('Tour 1', result)

    def test_render_tours_block(self):
        result = self.manager.render_tours_block()
        self.assertIn('css/tours.css', result)
        self.assertIn('css/pages.css', result)
        self.assertIn('<div class="tours">', result)