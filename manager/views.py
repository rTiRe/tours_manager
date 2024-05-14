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
