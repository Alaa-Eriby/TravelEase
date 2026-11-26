from rest_framework import serializers
from apps.hotels.models import Hotel, HotelRoom
from apps.destinations.serializers import DestinationSerializer

class HotelRoomSerializer(serializers.ModelSerializer):
    display_image = serializers.CharField(read_only=True)
    room_type_display = serializers.CharField(source='get_room_type_display', read_only=True)

    class Meta:
        model = HotelRoom
        fields = [
            'id', 'hotel', 'room_type', 'room_type_display', 'name', 'description',
            'capacity', 'price_per_night', 'total_rooms', 'image', 'image_url',
            'display_image', 'is_active'
        ]


class HotelSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    display_image = serializers.CharField(read_only=True)
    amenities_list = serializers.ListField(read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    rooms = HotelRoomSerializer(many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'destination', 'destination_details', 'address',
            'star_rating', 'description', 'amenities', 'amenities_list',
            'phone', 'email', 'image', 'image_url', 'display_image',
            'is_featured', 'min_price', 'rooms', 'created_at'
        ]
