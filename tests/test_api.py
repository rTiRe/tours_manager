"""Module with API tests."""

from os import getenv
from uuid import UUID

from django.contrib.auth.models import User
from django.db.models import Model
from django.db.models.base import ModelBase
from django.test import TestCase
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from django.core.exceptions import ValidationError

from manager.models import (Account, Address, Agency, City, Country, Review,
                            Tour)

ACCOUNT_NAME = 'disenfranchised_user'
NAME_LITERAL = 'name'

load_dotenv()
USER_NAME = getenv('DJANGO_TESTS_USER_NAME')
USER_PASSWORD = getenv('DJANGO_TESTS_USER_PASSWORD')
SUPERUSER_NAME = getenv('DJANGO_TESTS_SUPERUSER_NAME')
SUPERUSER_PASSWORD = getenv('DJANGO_TESTS_SUPERUSER_PASSWORD')


def create_many_to_many(model: Model, attrs_with_model: dict) -> Model:
    many_to_many = {}
    for field, attr in attrs_with_model.items():
        if isinstance(attr, list):
            many_to_many[field] = attrs_with_model[field]
    for field_to_pop in many_to_many.keys():
        attrs_with_model.pop(field_to_pop)
    created: Tour = model.objects.create(**attrs_with_model)
    for field_name, attrs in many_to_many.items():
        getattr(created, field_name).set(attrs)
    return created


def filter_many_to_many(json: dict) -> dict:
    json_copy = json.copy()
    fields_to_change = {}
    for field_key, field_data in json_copy.items():
        if isinstance(field_data, list):
            fields_to_change[field_key] = field_data
    for field_key, field_data in fields_to_change.items():
        json_copy.pop(field_key)
        json_copy[f'{field_key}__in'] = [field.id for field in field_data]
    return json_copy
        



def create_object(
    obj_model: Model,
    json: dict,
    return_json: bool = True,
) -> Model | dict:
    """Create object using json.

    Args:
        obj_model: Model - object model.
        json: dict - data for create object.
        return_json: bool, optional - return object as Model or as dict. Defaults to True.

    Returns:
        Model: model of created object.
        dict: json for created object.
    """
    json_copy = json.copy()
    for key, body in json_copy.items():
        if isinstance(body, list) and isinstance(body[0], ModelBase):
            model: Model = body[0]
            jsons = body[1]
            if isinstance(jsons, list):
                json_ob = [create_object(model, sub_json, return_json=False) for sub_json in jsons]
            else:
                json_ob = create_object(model, jsons, return_json=False)
            json_copy[key] = json_ob
    if not return_json:
        try:
            objects = obj_model.objects.filter(**json_copy)
        except ValidationError:
            json_for_filter = filter_many_to_many(json_copy)
            objects = obj_model.objects.filter(**json_for_filter)
        if objects.exists():
            return obj_model.objects.get(**json_copy)
        return create_many_to_many(obj_model, json_copy)
    return json_copy


def create_object_json_with_ids(object_with_model: dict) -> dict:
    """Create object with ids of child objects.

    Args:
        object_with_model: dict - object dict with models of child objects.

    Returns:
        dict: json for created object.
    """
    attrs_with_id = object_with_model.copy()
    for field, attrs in attrs_with_id.items():
        if isinstance(attrs, Model):
            attrs_with_id[field] = attrs.id
        if isinstance(attrs, list):
            attrs_with_id[field] = [attr.id for attr in attrs]
    return attrs_with_id


def get_object_as_superuser(
    model: Model,
    attrs_with_id: dict,
) -> UUID:
    """Get created object id as superuser.

    Args:
        model: Model - object model.
        attrs_with_id: dict - json data with child objects ids. Data for transform.

    Returns:
        UUID: finded object id.
    """
    if attrs_with_id.get('addresses'):
        attrs_with_id.pop('addresses')
    return model.objects.get(**attrs_with_id).id


def get_object_as_user(
    model: Model,
    attrs_with_model: dict,
) -> UUID:
    """Get created object id as user or create and return object id if not exists.

    Args:
        model: Model - object model.
        attrs_with_model: dict - json data with child objects models. Data for transform.

    Returns:
        UUID: finded object id.
    """
    try:
        created_id = model.objects.create(**attrs_with_model).id
    except TypeError:
        created = create_many_to_many(model, attrs_with_model)
        created_id = created.id
    return created_id


def get_object(
    model: Model,
    user: User,
    attrs_with_id: dict,
    attrs_with_model: dict,
) -> UUID:
    """Get created object id as user/superuser or create and return object id if not exists.

    Args:
        model: Model - object model.
        user: User - who want to get object.
        attrs_with_id: dict - json data with child objects ids. Data for transform.
        attrs_with_model: dict - json data with child objects models. Data for transform.

    Returns:
        UUID: finded object id.
    """
    if user.is_superuser:
        return get_object_as_superuser(model, attrs_with_id)
    return get_object_as_user(model, attrs_with_model)


def create_api_test(model: Model, url: str, creation_attrs: dict) -> TestCase:
    """Class decorator for create tests.

    Args:
        model: Model - object model.
        url: str - path to api.
        creation_attrs: dict - json data for create object for tests.

    Returns:
        TestCase: class with tests.
    """
    class ApiTest(TestCase):
        """API test class."""

        def setUp(self) -> None:
            """Pre-setup tests."""
            self.client = APIClient()
            self.user = User.objects.create_user(username=USER_NAME, password=USER_PASSWORD)
            self.superuser = User.objects.create_superuser(
                username=SUPERUSER_NAME,
                password=SUPERUSER_PASSWORD,
            )

        def manage(
            self,
            user: User,
            post_expected: int,
            put_expected: int,
            delete_expected: int,
        ) -> None:
            """Manage and run tests.

            Args:
                user: User - who run tests.
                post_expected: int - expected http code for post method.
                put_expected: int - expected http code for put method.
                delete_expected: int - expected http code for delete method.
            """
            token = Token(user=user)
            self.client.force_authenticate(user=user, token=token)
            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.head(url).status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.options(url).status_code, status.HTTP_200_OK)
            # if url == '/api/reviews/':
            #     print(creation_attrs)
            attrs_with_model = create_object(model, creation_attrs)
            attrs_with_id = create_object_json_with_ids(attrs_with_model)
            post_created = self.client.post(url, attrs_with_id)
            self.assertEqual(post_created.status_code, post_expected)
            created_id = get_object(model, user, attrs_with_id, attrs_with_model)
            put_response = self.client.put(f'{url}{created_id}/', attrs_with_id)
            self.assertEqual(put_response.status_code, put_expected)
            delete_response = self.client.delete(f'{url}{created_id}/', creation_attrs)
            self.assertEqual(delete_response.status_code, delete_expected)

        def test_superuser(self) -> None:
            """Run tests for superuser."""
            self.manage(
                self.superuser,
                post_expected=status.HTTP_201_CREATED,
                put_expected=status.HTTP_200_OK,
                delete_expected=status.HTTP_204_NO_CONTENT,
            )

        def test_user(self) -> None:
            """Run tests for user."""
            self.manage(
                self.user,
                post_expected=status.HTTP_403_FORBIDDEN,
                put_expected=status.HTTP_403_FORBIDDEN,
                delete_expected=status.HTTP_403_FORBIDDEN,
            )
    return ApiTest


url = '/api/'

country_data = {
    NAME_LITERAL: 'test_country',
}

city_data = {
    NAME_LITERAL: 'Тверь',
    'country': [Country, country_data],
    'point': 'SRID=4326;POINT (55.555555555555555 55.5555555555555)',
}

address_data = {
    'city': [City, city_data],
    'street': 'Пермская',
    'house_number': '47',
    'point': 'SRID=4326;POINT (55.555555555555555 55.5555555555555)',
}
AddressApiTest = create_api_test(Address, f'{url}addresses/', address_data)

agency_data = {
    NAME_LITERAL: 'test_agency',
    'phone_number': '+77777777777',
    'address': [Address, address_data],
}
AgencyApiTest = create_api_test(Agency, f'{url}agencies/', agency_data)

tour_data = {
    NAME_LITERAL: 'test_tour',
    'agency': [Agency, agency_data],
    'addresses': [Address, [address_data]],
    'starting_city': [City, city_data],
    'price': 4,
}
# print(tour_data)
TourApiTest = create_api_test(Tour, f'{url}tours/', tour_data)

user_data = {
    'username': 'test',
    'email': 'test@test.ru',
    'password': '1234509876qwerty',
}

account_data = {
    'account': [User, user_data],
    'is_agency': False,
}

review_data = {
    'tour': [Tour, tour_data],
    'account': [Account, account_data],
    'rating': 1.2,
    'text': 'test_review',
}

ReviewApiTest = create_api_test(Review, f'{url}reviews/', review_data)
