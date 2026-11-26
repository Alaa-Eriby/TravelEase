from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.bookings.models import PackageBooking, HotelBooking, BookingStatus
from apps.bookings.serializers import (
    PackageBookingSerializer, PackageBookingCreateSerializer,
    HotelBookingSerializer, HotelBookingCreateSerializer
)
from apps.payments.models import PaymentRecord
from apps.core.models import AuditLog, Notification

@login_required
def customer_dashboard_view(request):
    user = request.user
    today = timezone.now().date()

    # Package bookings
    all_package_bookings = user.package_bookings.select_related('departure__package', 'departure').prefetch_related('travelers')
    upcoming_packages = all_package_bookings.filter(status=BookingStatus.CONFIRMED, departure__departure_date__gte=today)
    past_packages = all_package_bookings.filter(status=BookingStatus.CONFIRMED, departure__departure_date__lt=today)
    cancelled_packages = all_package_bookings.filter(status=BookingStatus.CANCELLED)

    # Hotel bookings
    all_hotel_bookings = user.hotel_bookings.select_related('room__hotel', 'room')
    upcoming_hotels = all_hotel_bookings.filter(status=BookingStatus.CONFIRMED, check_in__gte=today)
    past_hotels = all_hotel_bookings.filter(status=BookingStatus.CONFIRMED, check_in__lt=today)
    cancelled_hotels = all_hotel_bookings.filter(status=BookingStatus.CANCELLED)

    # Favorites
    favorites = user.favorites.select_related('destination')

    # Payments
    payments = user.payments.all()[:10]

    # Metrics
    total_spent = sum(b.total_price for b in all_package_bookings.filter(status=BookingStatus.CONFIRMED)) + \
                  sum(b.total_price for b in all_hotel_bookings.filter(status=BookingStatus.CONFIRMED))

    return render(request, 'dashboard/customer/index.html', {
        'upcoming_packages': upcoming_packages,
        'past_packages': past_packages,
        'cancelled_packages': cancelled_packages,
        'upcoming_hotels': upcoming_hotels,
        'past_hotels': past_hotels,
        'cancelled_hotels': cancelled_hotels,
        'favorites': favorites,
        'payments': payments,
        'total_spent': total_spent,
        'total_bookings_count': all_package_bookings.count() + all_hotel_bookings.count(),
    })


@login_required
def package_confirmation_view(request, booking_reference):
    booking = get_object_or_404(
        PackageBooking.objects.select_related('departure__package__destination', 'customer').prefetch_related('travelers'),
        booking_reference=booking_reference
    )
    if not (request.user == booking.customer or request.user.is_staff or request.user.is_agent()):
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard_redirect')

    payment = PaymentRecord.objects.filter(booking_reference=booking.booking_reference).first()

    return render(request, 'dashboard/customer/package_confirmation.html', {
        'booking': booking,
        'payment': payment,
    })


@login_required
def hotel_confirmation_view(request, booking_reference):
    booking = get_object_or_404(
        HotelBooking.objects.select_related('room__hotel__destination', 'customer'),
        booking_reference=booking_reference
    )
    if not (request.user == booking.customer or request.user.is_staff):
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard_redirect')

    payment = PaymentRecord.objects.filter(booking_reference=booking.booking_reference).first()

    return render(request, 'dashboard/customer/hotel_confirmation.html', {
        'booking': booking,
        'payment': payment,
    })


@login_required
def cancel_package_booking_view(request, pk):
    booking = get_object_or_404(PackageBooking, pk=pk)

    if not (request.user == booking.customer or request.user.is_staff):
        messages.error(request, "You are not authorized to cancel this booking.")
        return redirect('bookings:customer_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by customer')
        try:
            booking.cancel(reason=reason)

            # Audit Log
            AuditLog.objects.create(
                user=request.user,
                action="BOOKING_CANCELLED",
                target_model="PackageBooking",
                target_id=str(booking.id),
                details=f"Package booking {booking.booking_reference} cancelled. Seats released."
            )

            # Notification
            Notification.objects.create(
                recipient=booking.customer,
                title="Booking Cancelled",
                message=f"Your booking {booking.booking_reference} has been cancelled per policy.",
                notification_type='warning'
            )

            messages.success(request, f"Booking {booking.booking_reference} has been cancelled successfully and reserved seats released.")
        except Exception as e:
            messages.error(request, f"Cancellation failed: {str(e)}")

    return redirect('bookings:customer_dashboard')


@login_required
def cancel_hotel_booking_view(request, pk):
    booking = get_object_or_404(HotelBooking, pk=pk)

    if not (request.user == booking.customer or request.user.is_staff):
        messages.error(request, "You are not authorized to cancel this reservation.")
        return redirect('bookings:customer_dashboard')

    if request.method == 'POST':
        reason = request.POST.get('reason', 'Cancelled by customer')
        try:
            booking.cancel(reason=reason)

            AuditLog.objects.create(
                user=request.user,
                action="HOTEL_BOOKING_CANCELLED",
                target_model="HotelBooking",
                target_id=str(booking.id),
                details=f"Hotel booking {booking.booking_reference} cancelled."
            )

            messages.success(request, f"Hotel reservation {booking.booking_reference} has been cancelled successfully.")
        except Exception as e:
            messages.error(request, f"Cancellation failed: {str(e)}")

    return redirect('bookings:customer_dashboard')


# --- REST API ViewSets ---

class PackageBookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_administrator():
            return PackageBooking.objects.all().select_related('departure__package', 'customer').prefetch_related('travelers')
        elif user.is_agent():
            return PackageBooking.objects.filter(departure__package__agent=user).select_related('departure__package', 'customer').prefetch_related('travelers')
        return PackageBooking.objects.filter(customer=user).select_related('departure__package', 'customer').prefetch_related('travelers')

    def get_serializer_class(self):
        if self.action == 'create':
            return PackageBookingCreateSerializer
        return PackageBookingSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        try:
            booking.cancel(reason=request.data.get('reason', 'Cancelled via API'))
            return Response({'status': 'Booking successfully cancelled and capacity updated.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HotelBookingViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_administrator():
            return HotelBooking.objects.all().select_related('room__hotel', 'customer')
        return HotelBooking.objects.filter(customer=user).select_related('room__hotel', 'customer')

    def get_serializer_class(self):
        if self.action == 'create':
            return HotelBookingCreateSerializer
        return HotelBookingSerializer

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        try:
            booking.cancel(reason=request.data.get('reason', 'Cancelled via API'))
            return Response({'status': 'Hotel booking cancelled successfully.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
