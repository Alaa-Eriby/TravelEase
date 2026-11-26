from django.contrib import admin
from apps.packages.models import TravelPackage, PackageDeparture

class PackageDepartureInline(admin.TabularInline):
    model = PackageDeparture
    extra = 1

@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ('title', 'destination', 'agent', 'duration_days', 'price_per_person', 'is_featured', 'is_active')
    list_filter = ('is_featured', 'is_active', 'destination__country')
    search_fields = ('title', 'description', 'destination__name', 'agent__username')
    inlines = [PackageDepartureInline]

@admin.register(PackageDeparture)
class PackageDepartureAdmin(admin.ModelAdmin):
    list_display = ('package', 'departure_date', 'return_date', 'total_capacity', 'booked_seats', 'available_seats', 'is_active')
    list_filter = ('is_active', 'departure_date')
    search_fields = ('package__title',)
