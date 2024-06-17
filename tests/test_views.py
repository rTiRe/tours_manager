from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from rest_framework import status

from manager.models import Account, Address, Agency, City, Country, Tour

POINT = -74.0061, 40.7129
PRICE = 400


def _get_tour_url(page_name: str, tour: Tour, url: str) -> str:
    if page_name == 'tour':
        url = f'{url}{tour.id}/'
    elif page_name == 'edit_tour':
        url = f'{url}{tour.id}/edit/'
    elif page_name == 'delete_tour':
        url = f'{url}{tour.id}/delete/'
    return url


def _get_url(
    page_name: str,
    page_url: str,
    tour: Tour,
    user: User,
    account: Account,
) -> tuple[str, str]:
    url = page_url
    if page_name == 'profile':
        username = page_url.split('/')[-2]
        reversed_url = reverse(page_name, kwargs={'username': username})
    elif page_name in {'tour', 'edit_tour', 'delete_tour'}:
        url = _get_tour_url(page_name, tour, url)
        reversed_url = reverse(page_name, kwargs={'uuid': tour.id})
    elif page_name == 'create_agency':
        user.is_staff = False
        user.save()
        account.agency = None
        account.save()
        reversed_url = reverse(page_name)
    else:
        reversed_url = reverse(page_name)
    return url, reversed_url


def create_successful_page_test(page_url: str, page_name: str, template: str, auth: bool = True):
    def test(self):
        self.client = Client()
        other_user = User.objects.create(username='other_user', password='user')
        user = None
        account = None
        tour = None
        Account.objects.create(account=other_user)
        if auth:
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
            tour = Tour.objects.create(
                name='Tour 1',
                description='Sample',
                agency=agency,
                price=PRICE,
                starting_city=city,
            )
            user = User.objects.create(username='user', password='user', is_staff=True)
            account = Account.objects.create(account=user, agency=agency)
            self.client.force_login(user)
        url, reversed_url = _get_url(page_name, page_url, tour, user, account)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template)
        response = self.client.get(reversed_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    return test


def create_redirect_page_test(page_name):
    def test(self):
        self.client = Client()
        self.client.logout()
        self.assertEqual(self.client.get(reverse(page_name)).status_code, status.HTTP_302_FOUND)
    return test


casual_pages = (
    ('', 'index', 'index.html', False),
    ('/tours/', 'tours', 'pages/tours.html', False),
    ('/agencies/', 'agencies', 'pages/agencies.html', False),
    ('/login/', 'manager-login', 'registration/login.html', False),
    ('/registration/', 'manager-registration', 'registration/registration.html', False),
    ('/profile/other_user/', 'profile', 'pages/profile.html', False),
)

casual_pages_methods = {
    f'test_{page}': create_successful_page_test(*page) for page in casual_pages
}
TestCasualPages = type('TestCasualPages', (TestCase,), casual_pages_methods)

auth_pages = (
    ('/profile/', 'my_profile', 'pages/profile.html'),
    ('/settings/', 'settings', 'pages/settings.html'),
    ('/profile/other_user/', 'profile', 'pages/profile.html'),
    ('/password_reset/', 'password_reset', 'registration/password_reset_form.html'),
    ('/password_change/', 'password_change', 'registration/password_change_form.html'),
    ('/tour/', 'tour', 'pages/tour.html'),
    ('/tour/', 'edit_tour', 'pages/edit_tour.html'),
    ('/tour/', 'delete_tour', 'pages/delete_tour.html'),
    ('/agencies/create/', 'create_agency', 'pages/create_agency.html'),
    ('/addresses/create/', 'create_address', 'pages/create_address.html'),
)

auth_pages_methods = {f'test_{page}': create_successful_page_test(*page) for page in auth_pages}
TestAuthPages = type('TestAuthPages', (TestCase,), auth_pages_methods)

redirect_pages = ('my_profile', 'settings')

redirect_pages_methods = {
    f'test_{page}': create_redirect_page_test(page) for page in redirect_pages
}
TestRedirectPages = type('TestRedirectPages', (TestCase,), redirect_pages_methods)
