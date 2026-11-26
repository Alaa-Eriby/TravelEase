from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from apps.hotels.models import Hotel, HotelRoom
from apps.hotels.serializers import HotelSerializer, HotelRoomSerializer
from apps.destinations.models import Destination
from apps.bookings.models import HotelBooking, BookingStatus
from apps.payments.models import PaymentRecord
from apps.core.models import Notification, AuditLog

def hotel_list_view(request):
    query = request.GET.get('q', '').strip()
    destination_id = request.GET.get('destination')
    star_rating = request.GET.get('star_rating')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    hotels = Hotel.objects.all().select_related('destination').prefetch_related('rooms')

    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query) |
            Q(destination__name__icontains=query)
        )

    if destination_id:
        hotels = hotels.filter(destination_id=destination_id)

    if star_rating:
        try:
            hotels = hotels.filter(star_rating=int(star_rating))
        except ValueError:
            pass

    if min_price:
        try:
            hotels = hotels.filter(rooms__price_per_night__gte=float(min_price)).distinct()
        except ValueError:
            pass

    if max_price:
        try:
            hotels = hotels.filter(rooms__price_per_night__lte=float(max_price)).distinct()
        except ValueError:
            pass

    destinations = Destination.objects.all()

    return render(request, 'hotels/list.html', {
        'hotels': hotels,
        'destinations': destinations,
        'selected_destination': destination_id,
        'star_rating': star_rating,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
    })


def hotel_detail_view(request, pk):
    hotel = get_object_or_404(Hotel.objects.select_related('destination'), pk=pk)
    rooms = hotel.rooms.filter(is_active=True)
    reviews = hotel.reviews.filter(is_approved=True).select_related('user')

    # Optional check_in check_out query params to show live room availability
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')
    rooms_availability = []

    for room in rooms:
        available_count = room.total_rooms
        if check_in_str and check_out_str:
            try:
                ci = datetime.strptime(check_in_str, '%Y-%m-%d').date()
                co = datetime.strptime(check_out_str, '%Y-%m-%d').date()
                if ci < co:
                    available_count = room.get_available_rooms_count(ci, co)
            except ValueError:
                pass
        rooms_availability.append({
            'room': room,
            'available_count': available_count
        })

    return render(request, 'hotels/detail.html', {
        'hotel': hotel,
        'rooms_availability': rooms_availability,
        'reviews': reviews,
        'check_in': check_in_str or '',
        'check_out': check_out_str or '',
    })


@login_required
def hotel_booking_view(request, room_id):
    room = get_object_or_404(HotelRoom.objects.select_related('hotel'), pk=room_id)

    if request.method == 'POST':
        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        guests_count = int(request.POST.get('guests_count', 1))
        rooms_count = int(request.POST.get('rooms_count', 1))
        special_requests = request.POST.get('special_requests', '')
        simulated_card = request.POST.get('card_number', '4242')

        try:
            check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
            check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            messages.error(request, "Please enter valid check-in and check-out dates.")
            return redirect('hotels:detail', pk=room.hotel.pk)

        if check_in < timezone.now().date():
            messages.error(request, "Check-in date cannot be in the past.")
            return redirect('hotels:detail', pk=room.hotel.pk)

        if check_in >= check_out:
            messages.error(request, "Check-out date must be after check-in date.")
            return redirect('hotels:detail', pk=room.hotel.pk)

        # Real database availability check preventing overlapping room reservations
        available_count = room.get_available_rooms_count(check_in, check_out)
        if available_count < rooms_count:
            messages.error(request, f"Sorry, this room is not available for the selected dates. Only {available_count} available.")
            return redirect('hotels:detail', pk=room.hotel.pk)

        nights = (check_out - check_in).days
        total_price = room.price_per_night * nights * rooms_count

        try:
            booking = HotelBooking.objects.create(
                customer=request.user,
                room=room,
                check_in=check_in,
                check_out=check_out,
                guests_count=guests_count,
                rooms_count=rooms_count,
                price_per_night=room.price_per_night,
                total_price=total_price,
                status=BookingStatus.CONFIRMED,
                special_requests=special_requests
            )

            # Simulated Safe Academic Payment Record
            PaymentRecord.objects.create(
                user=request.user,
                booking_type=PaymentRecord.BookingType.HOTEL,
                booking_reference=booking.booking_reference,
                amount=total_price,
                status=PaymentRecord.PaymentStatus.SUCCESS,
                card_last_four=simulated_card[-4:] if len(simulated_card) >= 4 else '4242'
            )

            # Notification
            Notification.objects.create(
                recipient=request.user,
                title="Hotel Reservation Confirmed!",
                message=f"Your stay at '{room.hotel.name}' ({room.name}) is confirmed. Ref: {booking.booking_reference}",
                notification_type='booking',
                link=f"/dashboard/bookings/hotel/{booking.id}/"
            )

            # Audit Log
            AuditLog.objects.create(
                user=request.user,
                action="HOTEL_BOOKED",
                target_model="HotelBooking",
                target_id=str(booking.id),
                details=f"Booked {rooms_count} room(s) at {room.hotel.name} from {check_in} to {check_out} for ${total_price}"
            )

            messages.success(request, f"Hotel reservation confirmed! Reference: {booking.booking_reference}")
            return redirect('bookings:hotel_confirmation', booking_reference=booking.booking_reference)

        except Exception as e:
            messages.error(request, f"Hotel reservation error: {str(e)}")
            return redirect('hotels:detail', pk=room.hotel.pk)

    return render(request, 'hotels/booking_form.html', {
        'room': room,
        'hotel': room.hotel,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
    })


# --- REST API ViewSets ---

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all().select_related('destination').prefetch_related('rooms')
    serializer_class = HotelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'address', 'destination__name', 'amenities']
    ordering_fields = ['star_rating', 'name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class HotelRoomViewSet(viewsets.ModelViewSet):
    queryset = HotelRoom.objects.filter(is_active=True).select_related('hotel')
    serializer_class = HotelRoomSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price_per_night', 'capacity']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
