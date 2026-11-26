from django.contrib import admin
from apps.destinations.models import Country, City, Destination, DestinationImage, Review, FavoriteDestination

class DestinationImageInline(admin.TabularInline):
    model = DestinationImage
    extra = 1

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'estimated_cost', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'country')
    search_fields = ('name', 'city__name', 'country__name', 'popular_attractions')
    inlines = [DestinationImageInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'destination', 'travel_package', 'hotel', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    search_fields = ('user__username', 'comment')

@admin.register(FavoriteDestination)
class FavoriteDestinationAdmin(admin.ModelAdmin):
    list_display = ('user', 'destination', 'created_at')
    search_fields = ('user__username', 'destination__name')
