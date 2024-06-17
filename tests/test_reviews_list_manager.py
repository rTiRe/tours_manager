from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import RequestFactory, TestCase

from manager.models import (Account, Address, Agency, City, Country, Review,
                            Tour)
from manager.views_utils.reviews_list_manager import ReviewsListManager

PRICE = 400
POINT = -74.0061, 40.7129


class ReviewsListManagerTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='tester', password='123')
        account = Account.objects.create(account=self.user)
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
        self.tour = Tour.objects.create(
            name='Tour 1', description='Sample', agency=agency, price=PRICE, starting_city=city,
        )
        self.review = Review.objects.create(tour=self.tour, rating=5, account=account)
        self.reviews = {self.tour: [self.review]}
        self.request = self.factory.get('/tour/{id}/#reviews'.format(id=self.tour.id))
        self.redirect_url = '/redirect/'

    def test_get_tour(self):
        manager = ReviewsListManager(self.request, self.reviews, self.redirect_url)
        tour = manager.get_tour()
        self.assertEqual(tour, self.tour)

    def test_render_review(self):
        manager = ReviewsListManager(self.request, self.reviews, self.redirect_url)
        render_result = manager.render_review(self.review, render_form=True)
        self.assertIn('<div class="review">', render_result)

    def test_review_form_post(self):
        form_data = {'rating': 4, 'text': 'Updated review text'}
        request = self.factory.post('/tour/{id}/reviews/'.format(id=self.tour.id), form_data)
        request.user = self.user
        manager = ReviewsListManager(request, self.reviews, self.redirect_url)
        manager.render_review(self.review, render_form=True)
        updated_review = Review.objects.get(id=self.review.id)
        self.assertEqual(updated_review.text, 'Updated review text')
        self.assertEqual(updated_review.rating, 4)

    def test_delete_review_post(self):
        request = self.factory.post(
            '/tour/{id}/reviews/'.format(id=self.tour.id), {'delete': self.review.id},
        )
        request.user = self.user
        manager = ReviewsListManager(request, self.reviews, self.redirect_url)
        manager.render_review(self.review, render_form=True)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
