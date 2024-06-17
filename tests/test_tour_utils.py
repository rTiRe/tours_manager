"""Tour utils tests."""

from django.contrib.gis.geos import Point
from django.test import RequestFactory, TestCase
from django.urls import reverse

from manager.forms import TourForm
from manager.models import Address, Agency, City, Country, Tour
from manager.views_utils.tour_utils import render_tour_form, save_tour

PRICE = 400
POINT = -74.0061, 40.7129


class TourFunctionTests(TestCase):
    """Tour functions tests."""

    def setUp(self):
        """Set up tests."""
        self.factory = RequestFactory()
        country = Country.objects.create(name='USA')
        city = City.objects.create(
            name='New York',
            country=country,
            point=Point(*POINT),
        )
        self.agency_address = Address.objects.create(
            city=city,
            street='Liberty St',
            house_number='1700',
            point=Point(*POINT),
        )
        self.agency = Agency.objects.create(
            name='TravelFun', phone_number='+79999999999', address=self.agency_address,
        )
        self.tour = Tour.objects.create(
            name='Sample Tour', agency=self.agency, starting_city=city, price=PRICE,
        )
        self.form_data = {
            'name': 'Updated Tour',
            'description': 'Updated Description',
            'agency': self.agency,
            'starting_city': city,
            'price': PRICE,
        }
        self.literals = {'title': 'Edit Tour', 'button': 'Save Changes', 'button_name': 'submit'}

    def test_save_tour_create(self):
        """Test saving a new tour using form data."""
        request = self.factory.post(reverse('create_tour'), self.form_data)
        form = TourForm(data=self.form_data)
        form.is_valid()
        new_tour = save_tour(request, None, form, self.form_data)
        self.assertIsInstance(new_tour, Tour)
        self.assertEqual(new_tour.name, 'Updated Tour')

    def test_render_tour_form_get(self):
        """Test rendering the tour form on GET request."""
        request = self.factory.get(
            reverse('edit_tour', kwargs={'uuid': self.tour.pk}),
        )
        rendered_form = render_tour_form(request, self.agency, {}, self.literals, self.tour)
        self.assertIn('form', rendered_form)

    def test_render_tour_form_post_valid(self):
        """Test POST request with valid form data to save tour."""
        post_data = self.form_data.copy()
        post_data.update({'agency': str(self.agency.id), 'addresses': []})
        request = self.factory.post(
            reverse('edit_tour', kwargs={'uuid': self.tour.pk}), post_data,
        )
        rendered_response = render_tour_form(request, self.agency, {}, self.literals, self.tour)
        self.assertIn('form', rendered_response)

    def test_render_tour_form_post_invalid(self):
        """Test POST request with invalid form data."""
        post_data = {'name': '', 'description': 'No name provided'}
        request = self.factory.post(
            reverse('edit_tour', kwargs={'uuid': self.tour.pk}), post_data,
        )
        rendered_response = render_tour_form(request, self.agency, {}, self.literals, self.tour)
        self.assertIn('errors', rendered_response)
