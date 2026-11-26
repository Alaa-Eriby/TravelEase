from rest_framework import serializers
from apps.destinations.models import Country, City, Destination, DestinationImage, Review, FavoriteDestination

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'description']


class CitySerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'name', 'country', 'country_name']


class DestinationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationImage
        fields = ['id', 'image', 'image_url', 'caption']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'username', 'destination', 'travel_package', 'hotel', 'rating', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'is_approved']


class DestinationSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    country_name = serializers.CharField(source='country.name', read_only=True)
    gallery_images = DestinationImageSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    display_image = serializers.CharField(read_only=True)

    class Meta:
        model = Destination
        fields = [
            'id', 'name', 'city', 'city_name', 'country', 'country_name',
            'description', 'popular_attractions', 'estimated_cost',
            'image', 'image_url', 'display_image', 'is_featured',
            'gallery_images', 'reviews_count', 'average_rating', 'created_at'
        ]

    def get_reviews_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 5.0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)


class FavoriteDestinationSerializer(serializers.ModelSerializer):
    destination = DestinationSerializer(read_only=True)
    destination_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FavoriteDestination
        fields = ['id', 'user', 'destination', 'destination_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
