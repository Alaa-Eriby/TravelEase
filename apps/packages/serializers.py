from rest_framework import serializers
from apps.packages.models import TravelPackage, PackageDeparture
from apps.destinations.serializers import DestinationSerializer

class PackageDepartureSerializer(serializers.ModelSerializer):
    available_seats = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PackageDeparture
        fields = [
            'id', 'package', 'departure_date', 'return_date',
            'total_capacity', 'booked_seats', 'available_seats',
            'price_override', 'current_price', 'is_active', 'is_available'
        ]
        read_only_fields = ['booked_seats']


class TravelPackageSerializer(serializers.ModelSerializer):
    destination_details = DestinationSerializer(source='destination', read_only=True)
    agent_name = serializers.CharField(source='agent.get_full_name', read_only=True)
    display_image = serializers.CharField(read_only=True)
    services_list = serializers.ListField(read_only=True)
    upcoming_departures = serializers.SerializerMethodField()

    class Meta:
        model = TravelPackage
        fields = [
            'id', 'title', 'agent', 'agent_name', 'destination', 'destination_details',
            'duration_days', 'price_per_person', 'description', 'included_services',
            'excluded_services', 'services_list', 'image', 'image_url', 'display_image',
            'is_featured', 'is_active', 'upcoming_departures', 'created_at'
        ]

    def get_upcoming_departures(self, obj):
        departures = obj.departures.filter(is_active=True).order_by('departure_date')[:5]
        return PackageDepartureSerializer(departures, many=True).data
