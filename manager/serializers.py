from rest_framework import serializers
from .models import Agency, Tour, Country, City, Address, Review, Account

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name', 'phone_number', 'address']


class CitySerializer(serializers.ModelSerializer):
    tours = serializers.PrimaryKeyRelatedField(queryset=Tour.objects.all(), many=True)
    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'tours', 'point']


class TourSerializer(serializers.ModelSerializer):
    cities = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), many=True)
    class Meta:
        model = Tour
        fields = ['id', 'name', 'agency', 'cities']
        optional_fields = ['description']


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'city',
            'street', 'house_number',
            'point',
        ]
        optional_fields = ['entrance_number', 'floor', 'flat_number',]


class ReviewSerializer(serializers.ModelSerializer):
    account = serializers.UUIDField(write_only=True)

    class Meta:
        model = Review
        fields = ['id', 'agency', 'account', 'rating', 'text']
