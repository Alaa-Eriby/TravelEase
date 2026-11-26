from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.destinations.models import Destination

class TravelPackage(models.Model):
    title = models.CharField(max_length=200)
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='managed_packages',
        help_text="Travel Agent responsible for this package"
    )
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='packages')
    duration_days = models.PositiveIntegerField(default=5)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    included_services = models.TextField(help_text="e.g. Flight, 4-star Hotel, Daily Breakfast, Guided Tour")
    excluded_services = models.TextField(blank=True, help_text="e.g. Personal expenses, Visa fees, Travel Insurance")
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.title} - ${self.price_per_person}"

    @property
    def display_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=800&q=80'

    @property
    def services_list(self):
        return [s.strip() for s in self.included_services.replace('\n', ',').split(',') if s.strip()]


class PackageDeparture(models.Model):
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='departures')
    departure_date = models.DateField()
    return_date = models.DateField()
    total_capacity = models.PositiveIntegerField(default=20)
    booked_seats = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['departure_date']
        unique_together = ('package', 'departure_date')

    def __str__(self):
        return f"{self.package.title} ({self.departure_date} to {self.return_date})"

    @property
    def current_price(self):
        return self.price_override if self.price_override is not None else self.package.price_per_person

    @property
    def available_seats(self):
        return max(0, self.total_capacity - self.booked_seats)

    @property
    def is_available(self):
        return self.is_active and self.departure_date >= timezone.now().date() and self.available_seats > 0

    def clean(self):
        if self.return_date and self.departure_date and self.return_date < self.departure_date:
            raise ValidationError("Return date cannot be earlier than departure date.")

    @classmethod
    @transaction.atomic
    def reserve_seats(cls, departure_id, seats_count):
        """
        Concurrency-safe reservation using select_for_update to strictly prevent overbooking.
        """
        dep = cls.objects.select_for_update().get(id=departure_id)
        if dep.available_seats < seats_count:
            raise ValidationError(f"Only {dep.available_seats} seat(s) available. Cannot reserve {seats_count}.")
        dep.booked_seats += seats_count
        dep.save(update_fields=['booked_seats'])
        return dep

    @classmethod
    @transaction.atomic
    def release_seats(cls, departure_id, seats_count):
        """
        Concurrency-safe seat release upon cancellation.
        """
        dep = cls.objects.select_for_update().get(id=departure_id)
        dep.booked_seats = max(0, dep.booked_seats - seats_count)
        dep.save(update_fields=['booked_seats'])
        return dep
