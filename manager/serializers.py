"""Data serializers for api."""

from rest_framework import serializers

from .models import Address, Agency, Country, Review, Tour

id_field = 'id'


class AgencySerializer(serializers.ModelSerializer):
    """Agency table serializer."""

    class Meta:
        """Class with Agency settings."""

        model = Agency
        fields = [id_field, 'name', 'phone_number', 'address']


class TourSerializer(serializers.ModelSerializer):
    """Tour table serializer."""

    addresses = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), many=True)

    class Meta:
        """Class with Tour settings."""

        model = Tour
        fields = [id_field, 'name', 'agency', 'addresses', 'starting_city', 'price']
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
        fields = ['id', 'tour', 'account', 'rating', 'text']
