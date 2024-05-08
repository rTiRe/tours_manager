from django.shortcuts import render
from django.http import QueryDict
from django.core import exceptions
from rest_framework import viewsets, permissions, authentication, request, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Agency, Tour, City, Country, Review, Address, Account
from .serializers import AgencySerializer, TourSerializer, CitySerializer, \
    CountrySerializer, ReviewSerializer, AddressSerializer, AccountSerializer
from django.utils.translation import gettext_lazy as _
from typing import Any
import json
from .validators import password_validator, username_validator, \
    user_fields_validator, name_validator
import re
from email_validate import validate


def index(request):
    return render(
        request,
        'index.html',
    )


class CustomViewSetPermission(permissions.BasePermission):
    _safe_methods = 'GET', 'HEAD', 'OPTIONS', 'TRACE'
    _unsafe_methods = 'PATCH', 'POST', 'PUT', 'DELETE'

    def has_permission(self, request, _):
        user = request.user
        if request.method in self._safe_methods and (user and user.is_authenticated):
            return True
        if request.method in self._unsafe_methods and (user and user.is_superuser):
            return True
        return False


def create_viewset(model_class, serializer):
    class CustomViewSet(viewsets.ModelViewSet):
        serializer_class = serializer
        queryset = model_class.objects.all()
        permission_classes = [CustomViewSetPermission]
        authentication_classes = [authentication.TokenAuthentication]
    return CustomViewSet


AgencyViewSet = create_viewset(Agency, AgencySerializer)
TourViewSet = create_viewset(Tour, TourSerializer)
CountryViewSet = create_viewset(Country, CountrySerializer)
CityViewSet = create_viewset(City, CitySerializer)
AddressViewSet = create_viewset(Address, AddressSerializer)
ReviewViewSet = create_viewset(Review, ReviewSerializer)


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    permission_classes = [CustomViewSetPermission]
    authentication_classes = [authentication.TokenAuthentication]

    def __create_user(self, data: request.Empty | dict | QueryDict | Any) -> User | Response:
        try:
            user_fields_validator(data)
        except exceptions.ValidationError as e:
            rule = r'\'(\w+)\': \'([\w\s]*)\''
            replaceable = json.loads(str(e))[0]
            replacement = '"\\g<1>": "\\g<2>"'
            replaced = re.sub(rule, replacement, replaceable, 0, re.MULTILINE)
            return Response(json.loads(replaced), status=status.HTTP_400_BAD_REQUEST)
        if not validate(data['email'], check_blacklist=False, check_dns=False, check_smtp=False):
            response_json = {'email': _('Incorrect email address.')}
            return Response(response_json, status=status.HTTP_400_BAD_REQUEST)
        username = data['username']
        try:
            username_validator(username)
        except (exceptions.ValidationError, ValueError) as e:
            return Response({'username': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        password = data['password']
        password2 = data['password2']
        try:
            password_validator(password, password2)
        except (exceptions.ValidationError, TypeError, ValueError) as e:
            rule = r'\'([\s\S]*?)\''
            replaceable = str(e)
            replacement = '"\\g<1>"'
            replaced = re.sub(rule, replacement, replaceable, 0, re.MULTILINE)
            print(replaced)
            try:
                e = json.loads(replaced)
            except json.decoder.JSONDecodeError:
                e = json.loads(f'"{replaced}"')
            return Response({'password': e}, status=status.HTTP_400_BAD_REQUEST)
        name_validator(data['first_name'], 'first')
        name_validator(data['last_name'], 'last')
        return User.objects.create_user(**data)

    def create(self, request: request.Request) -> Response:
        data = request.data
        try:
            is_agency = data.pop('is_agency')
        except KeyError:
            is_agency = False
        user = self.__create_user(data)
        if isinstance(user, Response):
            return user
        Account.objects.create(account=user, is_agency=is_agency)
        del data['password']
        data['is_agency'] = is_agency
        print(data)
        return Response(data, status=status.HTTP_201_CREATED)

