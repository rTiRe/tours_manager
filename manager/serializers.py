from rest_framework import serializers
from .models import Agency, Tour, City, Address, Review

class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ['id', 'name', 'phone_number', 'address']


class TourSerializer(serializers.ModelSerializer):
    cities = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), many=True)
    class Meta:
        model = Tour
        fields = ['id', 'name', 'agency', 'cities']
        optional_fields = ['description']


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
