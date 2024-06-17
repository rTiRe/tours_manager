from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import RequestFactory, TestCase

from manager.models import (Account, Address, Agency, City, Country, Review,
                            Tour)
from manager.views_utils.tours_list_manager import ToursListManager

PRICE = 400
POINT = -74.0061, 40.7129


class ToursListManagerTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/fake-url')
        user = User.objects.create_user(username='tester', password='123')
        account = Account.objects.create(account=user)
        country = Country.objects.create(name='USA')
        city = City.objects.create(
            name='New York',
            country=country,
            point=Point(*POINT),
        )
        agency_address = Address.objects.create(
            city=city,
            street='Liberty St',
            house_number='1700',
            point=Point(*POINT),
        )
        agency = Agency.objects.create(
            name='TravelFun',
            phone_number='+79999999999',
            address=agency_address,
        )
        self.tours = [
            Tour.objects.create(
                name=f'Tour {number}',
                description='Sample',
                agency=agency,
                price=PRICE,
                starting_city=city,
            )
            for number in range(5)
        ]
        self.reviews = {
            tour: [Review.objects.create(tour=tour, rating=5, account=account)]
            for tour in self.tours
        }
        self.manager = ToursListManager(self.request, self.tours, self.reviews)

    def test_initialization(self):
        self.assertIsInstance(self.manager, ToursListManager)
        self.assertEqual(len(self.manager.tours), 5)

    def test_render_tour_card(self):
        tour = self.tours[0]
        rating = 5
        render_result = self.manager.render_tour_card(tour, rating)
        self.assertIn(tour.name, render_result)
        self.assertNotIn('<span class="fa fa-star"></span>', render_result)

    def test_render_tours_list(self):
        render_result = self.manager.render_tours_list(1)
        self.assertIn('Tour 0', render_result)
        self.assertIn('Tour 1', render_result)

    def test_render_tours_block(self):
        render_result = self.manager.render_tours_block()
        self.assertIn('css/tours.css', render_result)
        self.assertIn('css/pages.css', render_result)
        self.assertIn('<div class="tours">', render_result)
