from datetime import datetime, timezone

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase

from manager.forms import AddressFormForCreate, ReviewForm
from manager.models import Account, Address, Agency, City, Country, Tour

POINT = -74.0061, 40.7129


class AddressFormFormCreateTest(TestCase):
    def test_valid_data(self):
        country = Country.objects.create(name='USA')
        city = City.objects.create(
            name='New York',
            country=country,
            point=Point(*POINT),
        )
        form = AddressFormForCreate(data={
            'city': city,
            'street': '123 Test St',
            'house_number': '12',
            'entrance_number': 1,
            'floor': 0,
            'flat_number': 101,
            'point': Point(*POINT),
        })
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        form = AddressFormForCreate(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('city', form.errors)

    def test_floor_negative(self):
        form = AddressFormForCreate(data={
            'floor': -2,
        })
        self.assertFalse(form.is_valid())


class ReviewFormTest(TestCase):
    def test_review_form_valid(self):
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
            name='TravelFun', phone_number='+79999999999', address=agency_address,
        )
        tour = Tour.objects.create(
            name='Tour 1', description='Sample', agency=agency, price=400, starting_city=city,
        )
        user = User.objects.create(username='user', password='user', is_staff=True)
        account = Account.objects.create(account=user, agency=agency)
        form = ReviewForm(data={
            'account': account,
            'tour': tour,
            'rating': 5,
            'text': 'Excellent experience!',
            'created': datetime.now(tz=timezone.utc),
        })
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        form = ReviewForm(data={
            'rating': 6,
            'text': 'Good!',
        })
        self.assertFalse(form.is_valid())

    def test_review_form_text_length(self):
        form = ReviewForm(data={
            'rating': 4,
            'text': 'a' * 1001,
        })
        self.assertFalse(form.is_valid())
