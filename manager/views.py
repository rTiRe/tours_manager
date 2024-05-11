import json
import re
from typing import Any

from django.contrib.auth.models import User
from django.core import exceptions
from django.http import QueryDict
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from email_validate import validate
from rest_framework import authentication, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.request import Request, Empty

from .models import Account, Address, Agency, City, Country, Review, Tour
from .serializers import (AccountSerializer, AddressSerializer,
                          AgencySerializer, CitySerializer, CountrySerializer,
                          ReviewSerializer, TourSerializer)
from .validators import (name_validator, password_validator,
                         user_fields_validator, username_validator)


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


class AccountViewSetPermission(permissions.BasePermission):
    def has_permission(self, request, _):
        user = request.user
        if user and user.is_superuser:
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
    permission_classes = [AccountViewSetPermission]
    authentication_classes = [authentication.TokenAuthentication]

    def replace_single_quote(
            self,
            replaceable: str,
            replacement: str = '"\\g<1>"',
            rule: str = r'\'([\s\S]*?)\''
    ) -> str:
        return re.sub(rule, replacement, replaceable, 0, re.MULTILINE)

    def __name_validator(self, data: Empty | dict | QueryDict | Any, names: list = ['first', 'last']) -> None | Response:
        for name in names:
            try:
                name_validator(data[f'{name}_name'], name)
            except (exceptions.ValidationError, ValueError, TypeError) as e:
                replaced = self.replace_single_quote(str(e))
                if type(e) == exceptions.ValidationError:
                    replaced = json.loads(replaced)[0]
                return Response({f'{name}_name': replaced}, status=status.HTTP_400_BAD_REQUEST)

    def __password_validator(self, data: Empty | dict | QueryDict | Any) -> None | Response:
        password = data.get('password', None)
        try:
            password2 = data.pop('password2')
        except KeyError:
            if password:
                return Response({'passwor2': 'field must be present'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                password2 = None
        try:
            password_validator(password, password2)
        except (exceptions.ValidationError, TypeError, ValueError) as e:
            replaced = self.replace_single_quote(str(e))
            try:
                e = json.loads(replaced)
                if len(e) == 1:
                    e = e[0]
            except json.decoder.JSONDecodeError:
                e = json.loads(f'"{replaced}"')
            return Response({'password': e}, status=status.HTTP_400_BAD_REQUEST)

    def __username_validator(
        self,
        data: Empty | dict | QueryDict | Any,
        ignore_existing_username: bool = False
    ) -> None | Response:
        username = data['username']
        try:
            username_validator(username, ignore_existing_username)
        except (exceptions.ValidationError, ValueError, TypeError) as e:
            replaced = self.replace_single_quote(str(e))
            if type(e) == exceptions.ValidationError:
                    replaced = json.loads(replaced)[0]
            return Response({'username': replaced}, status=status.HTTP_400_BAD_REQUEST)

    def __email_validator(self, data: Empty | dict | QueryDict | Any) -> None | Response:
        if not validate(data['email'], check_blacklist=False, check_dns=False, check_smtp=False):
            response_json = {'email': _('Incorrect email address.')}
            return Response(response_json, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(email=data['email']).exists():
            response_json = {'email': _('a user with this email already exists')}
            return Response(response_json, status=status.HTTP_400_BAD_REQUEST)

    def __fields_validator(self, data: Empty | dict | QueryDict | Any, check_required: bool = True) -> None | Response:
        try:
            user_fields_validator(data, check_required)
        except exceptions.ValidationError as e:
            replaced = self.replace_single_quote(
                json.loads(str(e))[0],
                '"\\g<1>": "\\g<2>"',
                r'\'(\w+)\': \'([\w\s]*)\''
            )
            return Response(json.loads(replaced), status=status.HTTP_400_BAD_REQUEST)

    def __get_is_agency(self, data: Empty | dict | QueryDict | Any) -> None | bool:
        try:
            is_agency = data.pop('is_agency')
        except KeyError:
            return False
        return is_agency

    def __user_validator(
        self,
        data: Empty | dict | QueryDict | Any,
        ignore_existing_username: bool = False,
        check_required: bool = True,
        partial: bool = False
    ) -> Response:
        validators = {
            self.__fields_validator: '',
            self.__email_validator: 'email',
            self.__username_validator: 'username',
            self.__password_validator: 'password',
            self.__name_validator: ['first', 'last'],
        }
        for validator in validators.keys():
            if partial:
                continue_validators = [
                    self.__email_validator,
                    self.__username_validator,
                    self.__password_validator
                ]
                if validator in continue_validators and not data.get(validators[validator]):
                    if validator == self.__password_validator and data.get('password2'):
                        return Response({'password': 'field must be present'}, status=status.HTTP_400_BAD_REQUEST)  

                    continue
                elif validator == self.__name_validator:
                    names = validators[validator]
                    if not data.get('first_name', None):
                        names.remove('first')
                    if not data.get('last_name', None):
                        names.remove('last')
            if validator == self.__fields_validator:
                validation_result = validator(data, check_required)
            elif validator == self.__username_validator:
                validation_result = validator(data, ignore_existing_username)
            elif validator == self.__name_validator:
                validation_result = validator(data, validators[validator])
            else:
                validation_result = validator(data)
            if validation_result:
                return validation_result

    def __create_user(self, data: Empty | dict | QueryDict | Any) -> User | Response:
        user_validation_result = self.__user_validator(data)
        if user_validation_result:
            return user_validation_result
        return User.objects.create_user(**data)

    def __update_user(
        self,
        user: User,
        data: Empty | dict | QueryDict | Any,
        ignore_existing_username: bool = False,
        check_required: bool = True,
        partial: bool = False
    ) -> User | Response:
        user_validation_result = self.__user_validator(
            data,
            ignore_existing_username,
            check_required=check_required,
            partial=partial
        )
        if user_validation_result:
            if user_validation_result.data == {'username': f'{user.username} already exists!'}:
                return self.__update_user(user, data, True, check_required=check_required, partial=partial)
            return user_validation_result
        try:
            password = data.pop('password')
        except KeyError:
            password = None
        if password and not user.check_password(password):
            user.set_password(password)
            user.save()
        if data.get('password2'):
            del data['password2']
        User.objects.filter(username=user.username).update(**data)
        if data.get('username'):
            username = data['username']
        else:
            username = user.username
        return User.objects.get(username=username)

    def update(self, request, check_required: bool = True, partial: bool = False, *args, **kwargs):
        data: dict = request.data
        is_agency = self.__get_is_agency(data)
        instance = self.get_object()
        user = self.__update_user(instance.account, data, check_required=check_required, partial=partial)
        if isinstance(user, Response):
            return user
        if data.get('email'):
            del data['email']
        update_data = {'account': user}
        if is_agency != None:
            data['is_agency'] = is_agency
            update_data['is_agency'] = is_agency
        Account.objects.filter(account=user).update(**update_data)
        return Response()

    def partial_update(self, request, *args, **kwargs) -> Response:
        return self.update(request, check_required=False, partial=True, *args, **kwargs)

    def create(self, request: Request) -> Response:
        data = request.data
        is_agency = self.__get_is_agency(data)
        user = self.__create_user(data)
        if isinstance(user, Response):
            return user
        Account.objects.create(account=user, is_agency=is_agency)
        del data['password']
        data['is_agency'] = is_agency
        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request: Request, *args, **kwargs) -> Response:
        self.get_object().account.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
