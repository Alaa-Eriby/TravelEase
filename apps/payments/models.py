import uuid
from django.db import models
from django.conf import settings

def generate_transaction_id():
    return f"TXN-SIM-{uuid.uuid4().hex[:10].upper()}"

class PaymentRecord(models.Model):
    class BookingType(models.TextChoices):
        PACKAGE = 'PACKAGE', 'Travel Package'
        HOTEL = 'HOTEL', 'Hotel Reservation'

    class PaymentMethod(models.TextChoices):
        CREDIT_CARD_SIM = 'CREDIT_CARD_SIM', 'Credit Card (Simulated)'
        PAYPAL_SIM = 'PAYPAL_SIM', 'PayPal (Simulated)'
        APPLE_PAY_SIM = 'APPLE_PAY_SIM', 'Apple Pay (Simulated)'

    class PaymentStatus(models.TextChoices):
        SUCCESS = 'SUCCESS', 'Payment Successful'
        PENDING = 'PENDING', 'Processing'
        FAILED = 'FAILED', 'Payment Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    transaction_id = models.CharField(max_length=40, unique=True, default=generate_transaction_id, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    booking_type = models.CharField(max_length=20, choices=BookingType.choices)
    booking_reference = models.CharField(max_length=50, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='USD')
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.CREDIT_CARD_SIM)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.SUCCESS)
    card_last_four = models.CharField(max_length=4, default='4242')
    is_demo_simulation = models.BooleanField(
        default=True,
        help_text="Explicit indicator confirming this is an academic safe simulation; no real monetary transfer occurred."
    )
    notes = models.CharField(max_length=255, default='Simulated Academic Transaction for Software Construction evaluation')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_id} - ${self.amount} ({self.status}) for {self.booking_reference}"
