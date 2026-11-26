from django.contrib import admin
from apps.bookings.models import PackageBooking, Traveler, HotelBooking

class TravelerInline(admin.TabularInline):
    model = Traveler
    extra = 0

@admin.register(PackageBooking)
class PackageBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'customer', 'departure', 'travelers_count', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking_reference', 'customer__username', 'departure__package__title')
    inlines = [TravelerInline]

@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'customer', 'room', 'check_in', 'check_out', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'check_in', 'created_at')
    search_fields = ('booking_reference', 'customer__username', 'room__hotel__name')

@admin.register(Traveler)
class TravelerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'passport_number', 'booking')
    search_fields = ('first_name', 'last_name', 'passport_number')
