"""Data serializers for api."""

from rest_framework import serializers

from .models import Address, Agency, City, Review, Tour

id_field = 'id'


class AgencySerializer(serializers.ModelSerializer):
    """Agency table serializer."""

    class Meta:
        """Class with Agency settings."""

        model = Agency
        fields = [id_field, 'name', 'phone_number', 'address']


class TourSerializer(serializers.ModelSerializer):
    """Tour table serializer."""

    cities = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), many=True)

    class Meta:
        """Class with Tour settings."""

        model = Tour
        fields = [id_field, 'name', 'agency', 'cities']
        optional_fields = ['description']


class AddressSerializer(serializers.ModelSerializer):
    """Address table serializer."""

    class Meta:
        """Class with Address setting."""

        model = Address
        fields = [
            id_field, 'city',
            'street', 'house_number',
            'point',
        ]
        optional_fields = ['entrance_number', 'floor', 'flat_number']


class ReviewSerializer(serializers.ModelSerializer):
    """Review table serializer."""

    class Meta:
        """Class with Review setting."""

        model = Review
        fields = ['id', 'agency', 'account', 'rating', 'text']
