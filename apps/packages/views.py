from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from apps.packages.models import TravelPackage, PackageDeparture
from apps.packages.serializers import TravelPackageSerializer, PackageDepartureSerializer
from apps.destinations.models import Destination
from apps.bookings.models import PackageBooking, Traveler, BookingStatus
from apps.payments.models import PaymentRecord
from apps.core.models import Notification, AuditLog

def package_list_view(request):
    query = request.GET.get('q', '').strip()
    destination_id = request.GET.get('destination')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    duration = request.GET.get('duration')

    packages = TravelPackage.objects.filter(is_active=True).select_related('destination', 'agent')

    if query:
        packages = packages.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(destination__name__icontains=query) |
            Q(destination__country__name__icontains=query)
        )

    if destination_id:
        packages = packages.filter(destination_id=destination_id)

    if min_price:
        try:
            packages = packages.filter(price_per_person__gte=float(min_price))
        except ValueError:
            pass

    if max_price:
        try:
            packages = packages.filter(price_per_person__lte=float(max_price))
        except ValueError:
            pass

    if duration:
        try:
            packages = packages.filter(duration_days=int(duration))
        except ValueError:
            pass

    destinations = Destination.objects.all()

    return render(request, 'packages/list.html', {
        'packages': packages,
        'destinations': destinations,
        'selected_destination': destination_id,
        'query': query,
        'min_price': min_price,
        'max_price': max_price,
        'duration': duration,
    })


def package_detail_view(request, pk):
    package = get_object_or_404(TravelPackage.objects.select_related('destination', 'agent'), pk=pk)
    departures = package.departures.filter(is_active=True, departure_date__gte=timezone.now().date()).order_by('departure_date')
    reviews = package.reviews.filter(is_approved=True).select_related('user')
    related_packages = TravelPackage.objects.filter(destination=package.destination, is_active=True).exclude(pk=package.pk)[:3]

    return render(request, 'packages/detail.html', {
        'package': package,
        'departures': departures,
        'reviews': reviews,
        'related_packages': related_packages,
    })


@login_required
def package_booking_wizard_view(request, pk):
    """
    12-Step Package Booking Module Implementation:
    Step 1-4: Package & Inclusions Display
    Step 5: Select Departure Date
    Step 6: Number of travelers
    Step 7: Enter traveler info
    Step 8: Real-time price calculation
    Step 9: Review reservation details
    Step 10: Confirmation & Simulated Safe Payment
    Step 11: Concurrency-safe Unique Reference Generation
    Step 12: Confirmation Page Display
    """
    package = get_object_or_404(TravelPackage, pk=pk)
    departures = package.departures.filter(is_active=True, departure_date__gte=timezone.now().date()).order_by('departure_date')

    if request.method == 'POST':
        departure_id = request.POST.get('departure_id')
        travelers_count = int(request.POST.get('travelers_count', 1))
        special_requests = request.POST.get('special_requests', '')
        simulated_card = request.POST.get('card_number', '4242')

        departure = get_object_or_404(PackageDeparture, pk=departure_id)

        if departure.available_seats < travelers_count:
            messages.error(request, f"Sorry! Only {departure.available_seats} seats remain on this departure date.")
            return redirect('packages:booking_wizard', pk=package.pk)

        unit_price = departure.current_price
        total_price = unit_price * travelers_count

        try:
            # Atomic reservation & seat deduction
            PackageDeparture.reserve_seats(departure.id, travelers_count)

            booking = PackageBooking.objects.create(
                customer=request.user,
                departure=departure,
                travelers_count=travelers_count,
                unit_price=unit_price,
                total_price=total_price,
                status=BookingStatus.CONFIRMED,
                special_requests=special_requests
            )

            # Extract individual traveler info
            for i in range(1, travelers_count + 1):
                first_name = request.POST.get(f'first_name_{i}') or request.user.first_name or f"Traveler {i}"
                last_name = request.POST.get(f'last_name_{i}') or request.user.last_name or ""
                passport = request.POST.get(f'passport_{i}', '')
                age = int(request.POST.get(f'age_{i}', 25) or 25)
                gender = request.POST.get(f'gender_{i}', 'M')

                Traveler.objects.create(
                    booking=booking,
                    first_name=first_name,
                    last_name=last_name,
                    passport_number=passport,
                    age=age,
                    gender=gender
                )

            # Simulated Safe Academic Payment Record
            PaymentRecord.objects.create(
                user=request.user,
                booking_type=PaymentRecord.BookingType.PACKAGE,
                booking_reference=booking.booking_reference,
                amount=total_price,
                status=PaymentRecord.PaymentStatus.SUCCESS,
                card_last_four=simulated_card[-4:] if len(simulated_card) >= 4 else '4242'
            )

            # Notification
            Notification.objects.create(
                recipient=request.user,
                title="Booking Confirmed!",
                message=f"Your trip '{package.title}' has been confirmed. Ref: {booking.booking_reference}",
                notification_type='booking',
                link=f"/dashboard/bookings/package/{booking.id}/"
            )

            # Audit Log
            AuditLog.objects.create(
                user=request.user,
                action="PACKAGE_BOOKED",
                target_model="PackageBooking",
                target_id=str(booking.id),
                details=f"Booked {travelers_count} seats on {departure.departure_date} for ${total_price}"
            )

            messages.success(request, f"Booking successfully confirmed! Reference: {booking.booking_reference}")
            return redirect('bookings:package_confirmation', booking_reference=booking.booking_reference)

        except Exception as e:
            messages.error(request, f"Reservation error: {str(e)}")
            return redirect('packages:booking_wizard', pk=package.pk)

    return render(request, 'packages/booking_wizard.html', {
        'package': package,
        'departures': departures,
    })


# --- REST API ViewSets ---

class TravelPackageViewSet(viewsets.ModelViewSet):
    queryset = TravelPackage.objects.filter(is_active=True).select_related('destination', 'agent')
    serializer_class = TravelPackageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'destination__name', 'destination__country__name']
    ordering_fields = ['price_per_person', 'duration_days', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]


class PackageDepartureViewSet(viewsets.ModelViewSet):
    queryset = PackageDeparture.objects.filter(is_active=True)
    serializer_class = PackageDepartureSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['departure_date', 'price_override']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
