from django.contrib import admin
from apps.payments.models import PaymentRecord

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'booking_reference', 'booking_type', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'booking_type', 'payment_method')
    search_fields = ('transaction_id', 'booking_reference', 'user__username')
