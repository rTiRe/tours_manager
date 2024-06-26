"""Models tests."""

from django.contrib.gis.geos import Point
from django.test import TestCase

from manager.models import Address, Agency, City, Country, Tour

PRICE = 400


class CountryModelTest(TestCase):
    """Country model tests class."""

    def test_create_country(self):
        """Test create country."""
        country = Country.objects.create(name='Russia')
        self.assertEqual(country.name, 'Russia')

    def test_string_representation(self):
        """Test string representation."""
        country = Country(name='France')
        self.assertEqual(str(country), 'France')


class CityModelTest(TestCase):
    """City model tests class."""

    def setUp(self):
        """Set up first tests."""
        self.country = Country.objects.create(name='Germany')

    def test_create_city(self):
        """Test create city."""
        city = City.objects.create(
            name='Berlin',
            country=self.country,
            point=Point(13.405, 52.52),
        )
        self.assertEqual(city.name, 'Berlin')
        self.assertEqual(city.country, self.country)

    def test_string_representation(self):
        """Test string representation."""
        city = City(
            name='Munich',
            country=self.country,
            point=Point(11.576124, 48.137154),
        )
        expected_string = f'{city.name}, {city.country}'
        self.assertEqual(str(city), expected_string)


class AgencyModelTest(TestCase):
    """Agency model tests class."""

    def setUp(self):
        """Set up first tests."""
        country = Country.objects.create(name='USA')
        city = City.objects.create(
            name='New York',
            country=country,
            point=Point(-74.006, 40.7128),
        )
        self.address = Address.objects.create(
            city=city,
            street='Liberty St',
            house_number='1700',
            point=Point(-74.0061, 40.7129),
        )

    def test_agency_creation(self):
        """Tests agency creation."""
        Agency.objects.create(name='TravelFun', phone_number='+79999999999', address=self.address)


class AddressModelTest(TestCase):
    """Address model tests class."""

    def setUp(self):
        """Set up tests."""
        country = Country.objects.create(name='USA')
        self.city = City.objects.create(
            name='New York',
            country=country,
            point=Point(-74.006, 40.7128),
        )

    def test_address_creation(self):
        """Test address creation."""
        address = Address.objects.create(
            city=self.city,
            street='Wall Street',
            house_number='12',
            point=Point(-74.0061, 40.7129),
        )
        self.assertEqual(address.city, self.city)
        self.assertEqual(address.street, 'Wall Street')
        self.assertEqual(address.house_number, '12')


class TourModelTest(TestCase):
    """Tours Models tests class."""

    def setUp(self):
        """Set up tests."""
        country = Country.objects.create(name='USA')
        self.city = City.objects.create(
            name='New York',
            country=country,
            point=Point(-74.006, 40.7128),
        )
        agency_address = Address.objects.create(
            city=self.city,
            street='Liberty St',
            house_number='1700',
            point=Point(-74.0061, 40.7129),
        )
        self.agency = Agency.objects.create(
            name='TravelFun', phone_number='+79999999999', address=agency_address,
        )
        self.address = Address.objects.create(
            city=self.city,
            street='Liberty St',
            house_number='1701',
            point=Point(-74.0062, 40.713),
        )

    def test_tour_creation(self):
        """Test tour creation."""
        tour = Tour.objects.create(
            name='Exciting NY Tour',
            description='Discover NY with us!',
            agency=self.agency,
            starting_city=self.city,
            price=PRICE,
        )
        self.assertEqual(tour.name, 'Exciting NY Tour')
        self.assertEqual(tour.description, 'Discover NY with us!')
        self.assertEqual(tour.agency, self.agency)
