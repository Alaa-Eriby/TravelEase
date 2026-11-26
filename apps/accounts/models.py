from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Customer / Traveler')
        AGENT = 'AGENT', _('Travel Agent / Provider')
        ADMIN = 'ADMIN', _('Administrator')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    def is_agent(self):
        return self.role == self.Role.AGENT

    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    passport_number = models.CharField(max_length=50, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"Customer Profile: {self.user.get_full_name() or self.user.username}"


class TravelAgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    agency_name = models.CharField(max_length=150)
    license_number = models.CharField(max_length=100, unique=True)
    business_email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)

    def __str__(self):
        return f"Agent: {self.agency_name} ({self.user.username})"
