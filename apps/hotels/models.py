from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.destinations.models import Destination

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='hotels')
    address = models.CharField(max_length=255)
    star_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], default=4)
    description = models.TextField()
    amenities = models.TextField(help_text="e.g. Free Wi-Fi, Swimming Pool, Spa, Airport Shuttle, Gym, Breakfast included")
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'name']

    def __str__(self):
        return f"{self.name} ({self.star_rating}★) - {self.destination.name}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80'

    @property
    def amenities_list(self):
        return [a.strip() for a in self.amenities.replace('\n', ',').split(',') if a.strip()]

    @property
    def min_price(self):
        cheapest_room = self.rooms.filter(is_active=True).order_by('price_per_night').first()
        return cheapest_room.price_per_night if cheapest_room else 0.00


class HotelRoom(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = 'SINGLE', 'Single Room'
        DOUBLE = 'DOUBLE', 'Double Room'
        DELUXE = 'DELUXE', 'Deluxe Suite'
        FAMILY = 'FAMILY', 'Family Suite'
        PRESIDENTIAL = 'PRESIDENTIAL', 'Presidential Suite'

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.DOUBLE)
    name = models.CharField(max_length=150, help_text="e.g. Executive Sea View King Room")
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=2, help_text="Max adults / guests")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=10, help_text="Total inventory count for this room category")
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['price_per_night']

    def __str__(self):
        return f"{self.hotel.name} - {self.name} (${self.price_per_night}/night)"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80'

    def get_available_rooms_count(self, check_in, check_out):
        """
        Calculates available rooms for the specified date range by querying active overlapping bookings.
        """
        from apps.bookings.models import HotelBooking
        overlapping_bookings = HotelBooking.objects.filter(
            room=self,
            status__in=['PENDING', 'CONFIRMED'],
            check_in__lt=check_out,
            check_out__gt=check_in
        ).count()
        return max(0, self.total_rooms - overlapping_bookings)
