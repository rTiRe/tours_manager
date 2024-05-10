from rest_framework import serializers
from .models import Agency, Tour, Country, City, Address, Review, Account

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name', 'phone_number', 'address']


class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = ['id', 'name', 'description', 'agency', 'cities']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'tours', 'point']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'city',
            'street', 'house_number',
            'entrance_number', 'floor',
            'flat_number', 'point',
        ]


class ReviewSerializer(serializers.ModelSerializer):
    account = serializers.UUIDField(write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'agency', 'account', 'rating', 'text']


class AccountSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source = 'account.first_name')
    last_name = serializers.CharField(source = 'account.last_name')
    username = serializers.CharField(source = 'account.username')
    password = serializers.CharField(source = 'account.password', write_only=True)

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'username', 'is_agency', 'password']
        extra_kwargs = {'password': {'write_only': True}}
