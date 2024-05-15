from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.db.models import Model
from django.db.models.base import ModelBase

from manager.models import Agency, Tour, Country, City, Address, Account, Review

ACCOUNT_NAME = 'disenfranchised_user'

def create_object(
        obj_model: Model,
        json: dict,
        return_json: bool = True,
) -> Model:
    json_copy = json.copy()
    for key, value in json_copy.items():
        if isinstance(value, list) and isinstance(value[0], ModelBase):
            sub_model: Model = value[0]
            sub_jsons = value[1]
            if isinstance(sub_jsons, list):
                object = [create_object(sub_model, sub_json, False) for sub_json in sub_jsons]
            else:
                object = create_object(sub_model, sub_jsons, False)
            json_copy[key] = object
    if not return_json:
        if obj_model.objects.filter(**json_copy).exists():
            return obj_model.objects.get(**json_copy)
        else:
            return obj_model.objects.create(**json_copy)
    return json_copy

def create_api_test(model: Model, url: str, creation_attrs: dict):
    class ApiTest(TestCase):
        def setUp(self) -> None:
            self.client = APIClient()
            self.user = User.objects.create_user(username='abc', password='abc')
            self.superuser = User.objects.create_superuser(username='admin', password='admin')
            self.user_token = Token(user=self.user)
            self.superuser_token = Token(user=self.superuser)

        def manage(
            self, user: User, token: Token,
            post_expected: int,
            put_expected: int,
            delete_expected: int,
        ):
            self.client.force_authenticate(user=user, token=token)

            self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.head(url).status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.options(url).status_code, status.HTTP_200_OK)
            attrs_with_model = create_object(model, creation_attrs)
            attrs_with_id = attrs_with_model.copy()
            for field, attrs in attrs_with_id.items():
                if isinstance(attrs, Model):
                    attrs_with_id[field] = attrs.id
                if isinstance(attrs, list):
                    attrs_with_id[field] = [attr.id for attr in attrs]
            post_created = self.client.post(url, attrs_with_id)
            self.assertEqual(post_created.status_code, post_expected)
            if user.is_superuser:
                if attrs_with_id.get('cities'):
                    attrs_with_id.pop('cities')
                created_id = model.objects.get(**attrs_with_id).id
            else:
                try:
                    created_id = model.objects.create(**attrs_with_model).id
                except TypeError:
                    many_to_many = {}
                    for field, attr in attrs_with_model.items():
                        if isinstance(attr, list):
                            many_to_many[field] = attrs_with_model[field]
                    for field in many_to_many.keys():
                        attrs_with_model.pop(field)
                    created: Tour = model.objects.create(**attrs_with_model)
                    for field, attrs in many_to_many.items():
                        getattr(created, field).set(attrs)
                    created_id = created.id
            instance_url = f'{url}{created_id}/'
            put_response = self.client.put(instance_url, attrs_with_id)
            self.assertEqual(put_response.status_code, put_expected)

            delete_response = self.client.delete(instance_url, creation_attrs)
            self.assertEqual(delete_response.status_code, delete_expected)

        def test_superuser(self):
            self.manage(
                self.superuser, self.superuser_token,
                post_expected=status.HTTP_201_CREATED,
                put_expected=status.HTTP_200_OK,
                delete_expected=status.HTTP_204_NO_CONTENT,
            )

        def test_user(self):
            self.manage(
                self.user, self.user_token,
                post_expected=status.HTTP_403_FORBIDDEN,
                put_expected=status.HTTP_403_FORBIDDEN,
                delete_expected=status.HTTP_403_FORBIDDEN,
            )
    return ApiTest


url = '/api/'
