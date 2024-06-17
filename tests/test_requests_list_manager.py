"""Requests manager tests."""

from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import RequestFactory, TestCase
from django.urls import reverse
from rest_framework import status

from manager.models import (Account, Address, Agency, AgencyRequests, City,
                            Country)
from manager.views_utils.requests_list_manager import AgencyRequestsListManager

POINT = -74.0061, 40.7129


class AgencyRequestsListManagerTest(TestCase):
    """Requests manager tests."""

    def setUp(self):
        """Set up tests."""
        self.factory = RequestFactory()
        user = User.objects.create_user(username='tester', password='123')
        self.account = Account.objects.create(account=user)
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
        self.agency_request = AgencyRequests.objects.create(account=self.account, agency=agency)
        self.agency_requests = [self.agency_request]
        self.request = self.factory.get('/fake-url')

    def test_initialization(self):
        """Test that the manager initializes correctly."""
        manager = AgencyRequestsListManager(self.request, self.agency_requests)
        self.assertIsInstance(manager, AgencyRequestsListManager)

    def test_render_agency_request_card(self):
        """Test rendering of a single agency request card."""
        manager = AgencyRequestsListManager(self.request, self.agency_requests)
        rendered_card = manager.render_agency_request_card(self.agency_request)
        self.assertIn('<div class="card">', rendered_card)

    def test_render_agency_requests_list(self):
        """Test rendering of the agency requests list."""
        manager = AgencyRequestsListManager(self.request, self.agency_requests)
        rendered_list = manager.render_agency_requests_list(1)
        self.assertIn('<div class="card">', rendered_list)

    def test_post_accept_agency_request(self):
        """Test handling of accepting an agency request via POST."""
        request = self.factory.post(
            reverse('my_profile'), {'accept': 'true', 'id': str(self.account.id)},
        )
        manager = AgencyRequestsListManager(request, self.agency_requests)
        response = manager.render_agency_requests_block()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(AgencyRequests.objects.filter(id=self.agency_request.id).exists())

    def test_post_decline_agency_request(self):
        """Test handling of declining an agency request via POST."""
        request = self.factory.post(
            reverse('my_profile'), {'decline': 'true', 'id': str(self.account.id)},
        )
        manager = AgencyRequestsListManager(request, self.agency_requests)
        response = manager.render_agency_requests_block()
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertFalse(AgencyRequests.objects.filter(id=self.agency_request.id).exists())
