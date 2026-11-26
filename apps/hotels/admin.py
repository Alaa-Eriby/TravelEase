from django.contrib import admin
from apps.hotels.models import Hotel, HotelRoom

class HotelRoomInline(admin.TabularInline):
    model = HotelRoom
    extra = 1

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'star_rating', 'phone', 'is_featured')
    list_filter = ('star_rating', 'is_featured', 'destination__country')
    search_fields = ('name', 'address', 'destination__name')
    inlines = [HotelRoomInline]

@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'room_type', 'capacity', 'price_per_night', 'total_rooms', 'is_active')
    list_filter = ('room_type', 'is_active')
    search_fields = ('name', 'hotel__name')
