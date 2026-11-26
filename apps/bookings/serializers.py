from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.bookings.models import PackageBooking, Traveler, HotelBooking, BookingStatus
from apps.packages.models import PackageDeparture
from apps.hotels.models import HotelRoom
from apps.packages.serializers import PackageDepartureSerializer
from apps.hotels.serializers import HotelRoomSerializer
from apps.payments.models import PaymentRecord

class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = ['id', 'first_name', 'last_name', 'passport_number', 'age', 'gender']


class PackageBookingSerializer(serializers.ModelSerializer):
    departure_details = PackageDepartureSerializer(source='departure', read_only=True)
    travelers = TravelerSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    package_title = serializers.CharField(source='departure.package.title', read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)

    class Meta:
        model = PackageBooking
        fields = [
            'id', 'booking_reference', 'customer', 'customer_name', 'departure',
            'departure_details', 'package_title', 'travelers_count', 'unit_price',
            'total_price', 'status', 'special_requests', 'can_cancel',
            'cancellation_reason', 'cancelled_at', 'travelers', 'created_at'
        ]
        read_only_fields = ['id', 'booking_reference', 'customer', 'unit_price', 'total_price', 'status', 'created_at']


class PackageBookingCreateSerializer(serializers.Serializer):
    departure_id = serializers.IntegerField()
    special_requests = serializers.CharField(required=False, allow_blank=True)
    travelers = TravelerSerializer(many=True)
    simulated_card_last4 = serializers.CharField(required=False, default='4242')

    def validate(self, attrs):
        departure_id = attrs.get('departure_id')
        travelers = attrs.get('travelers')
        if not travelers:
            raise serializers.ValidationError("At least one traveler must be provided.")
        
        try:
            dep = PackageDeparture.objects.get(id=departure_id)
        except PackageDeparture.DoesNotExist:
            raise serializers.ValidationError("Selected package departure does not exist.")

        if dep.departure_date < timezone.now().date():
            raise serializers.ValidationError("Cannot book a trip departure that has already passed.")

        if dep.available_seats < len(travelers):
            raise serializers.ValidationError(f"Insufficient capacity! Only {dep.available_seats} seat(s) remaining.")

        attrs['departure'] = dep
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        departure = validated_data['departure']
        travelers_data = validated_data['travelers']
        special_requests = validated_data.get('special_requests', '')
        user = self.context['request'].user
        simulated_card = validated_data.get('simulated_card_last4', '4242')

        count = len(travelers_data)
        unit_price = departure.current_price
        total_price = unit_price * count

        # Concurrency-safe seat reservation with select_for_update
        PackageDeparture.reserve_seats(departure.id, count)

        booking = PackageBooking.objects.create(
            customer=user,
            departure=departure,
            travelers_count=count,
            unit_price=unit_price,
            total_price=total_price,
            status=BookingStatus.CONFIRMED,
            special_requests=special_requests
        )

        for t_data in travelers_data:
            Traveler.objects.create(booking=booking, **t_data)

        # Create academic simulated payment record
        PaymentRecord.objects.create(
            user=user,
            booking_type=PaymentRecord.BookingType.PACKAGE,
            booking_reference=booking.booking_reference,
            amount=total_price,
            status=PaymentRecord.PaymentStatus.SUCCESS,
            card_last_four=simulated_card[-4:] if len(simulated_card) >= 4 else '4242'
        )

        return booking


class HotelBookingSerializer(serializers.ModelSerializer):
    room_details = HotelRoomSerializer(source='room', read_only=True)
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    hotel_name = serializers.CharField(source='room.hotel.name', read_only=True)
    total_nights = serializers.IntegerField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)

    class Meta:
        model = HotelBooking
        fields = [
            'id', 'booking_reference', 'customer', 'customer_name', 'room',
            'room_details', 'hotel_name', 'check_in', 'check_out', 'guests_count',
            'rooms_count', 'price_per_night', 'total_nights', 'total_price',
            'status', 'special_requests', 'can_cancel', 'cancellation_reason',
            'cancelled_at', 'created_at'
        ]
        read_only_fields = ['id', 'booking_reference', 'customer', 'price_per_night', 'total_price', 'status', 'created_at']


class HotelBookingCreateSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    guests_count = serializers.IntegerField(default=1, min_value=1)
    rooms_count = serializers.IntegerField(default=1, min_value=1)
    special_requests = serializers.CharField(required=False, allow_blank=True)
    simulated_card_last4 = serializers.CharField(required=False, default='4242')

    def validate(self, attrs):
        room_id = attrs['room_id']
        check_in = attrs['check_in']
        check_out = attrs['check_out']
        rooms_count = attrs.get('rooms_count', 1)

        if check_in >= check_out:
            raise serializers.ValidationError("Check-out date must be strictly after check-in date.")

        if check_in < timezone.now().date():
            raise serializers.ValidationError("Check-in date cannot be in the past.")

        try:
            room = HotelRoom.objects.get(id=room_id, is_active=True)
        except HotelRoom.DoesNotExist:
            raise serializers.ValidationError("Selected hotel room is not active or does not exist.")

        available_count = room.get_available_rooms_count(check_in, check_out)
        if available_count < rooms_count:
            raise serializers.ValidationError(f"Selected room category is sold out for these dates! Only {available_count} available.")

        attrs['room'] = room
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        room = validated_data['room']
        check_in = validated_data['check_in']
        check_out = validated_data['check_out']
        guests_count = validated_data['guests_count']
        rooms_count = validated_data.get('rooms_count', 1)
        special_requests = validated_data.get('special_requests', '')
        user = self.context['request'].user
        simulated_card = validated_data.get('simulated_card_last4', '4242')

        nights = max(1, (check_out - check_in).days)
        price_per_night = room.price_per_night
        total_price = price_per_night * nights * rooms_count

        booking = HotelBooking.objects.create(
            customer=user,
            room=room,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests_count,
            rooms_count=rooms_count,
            price_per_night=price_per_night,
            total_price=total_price,
            status=BookingStatus.CONFIRMED,
            special_requests=special_requests
        )

        PaymentRecord.objects.create(
            user=user,
            booking_type=PaymentRecord.BookingType.HOTEL,
            booking_reference=booking.booking_reference,
            amount=total_price,
            status=PaymentRecord.PaymentStatus.SUCCESS,
            card_last_four=simulated_card[-4:] if len(simulated_card) >= 4 else '4242'
        )

        return booking
