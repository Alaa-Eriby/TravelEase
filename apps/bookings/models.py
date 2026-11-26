import uuid
from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.packages.models import PackageDeparture
from apps.hotels.models import HotelRoom

def generate_package_reference():
    return f"TE-PKG-{uuid.uuid4().hex[:8].upper()}"

def generate_hotel_reference():
    return f"TE-HTL-{uuid.uuid4().hex[:8].upper()}"


class BookingStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Confirmation'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'


class PackageBooking(models.Model):
    booking_reference = models.CharField(max_length=30, unique=True, default=generate_package_reference, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='package_bookings')
    departure = models.ForeignKey(PackageDeparture, on_delete=models.PROTECT, related_name='bookings')
    travelers_count = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.CONFIRMED)
    special_requests = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_reference} - {self.departure.package.title} ({self.customer.username})"

    @property
    def can_cancel(self):
        # Allow cancellation if not already cancelled and departure date is in the future
        if self.status == BookingStatus.CANCELLED:
            return False
        return self.departure.departure_date > timezone.now().date()

    @transaction.atomic
    def cancel(self, reason="Customer requested cancellation"):
        if not self.can_cancel:
            raise ValidationError("This booking cannot be cancelled because it has already started, passed, or is already cancelled.")
        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_at = timezone.now()
        self.save(update_fields=['status', 'cancellation_reason', 'cancelled_at', 'updated_at'])
        # Concurrency-safe release of seats
        PackageDeparture.release_seats(self.departure.id, self.travelers_count)
        return True


class Traveler(models.Model):
    booking = models.ForeignKey(PackageBooking, on_delete=models.CASCADE, related_name='travelers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(default=25)
    gender = models.CharField(max_length=20, choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')), default='M')

    def __str__(self):
        return f"{self.first_name} {self.last_name} (Ref: {self.booking.booking_reference})"


class HotelBooking(models.Model):
    booking_reference = models.CharField(max_length=30, unique=True, default=generate_hotel_reference, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hotel_bookings')
    room = models.ForeignKey(HotelRoom, on_delete=models.PROTECT, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests_count = models.PositiveIntegerField(default=1)
    rooms_count = models.PositiveIntegerField(default=1)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.CONFIRMED)
    special_requests = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.booking_reference} - {self.room.hotel.name} ({self.customer.username})"

    @property
    def total_nights(self):
        return max(1, (self.check_out - self.check_in).days)

    @property
    def can_cancel(self):
        if self.status == BookingStatus.CANCELLED:
            return False
        return self.check_in > timezone.now().date()

    @transaction.atomic
    def cancel(self, reason="Customer requested cancellation"):
        if not self.can_cancel:
            raise ValidationError("This hotel reservation cannot be cancelled because check-in date has passed or booking is already cancelled.")
        self.status = BookingStatus.CANCELLED
        self.cancellation_reason = reason
        self.cancelled_at = timezone.now()
        self.save(update_fields=['status', 'cancellation_reason', 'cancelled_at', 'updated_at'])
        return True
