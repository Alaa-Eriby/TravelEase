from rest_framework import serializers
from apps.payments.models import PaymentRecord

class PaymentRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'transaction_id', 'user', 'username', 'booking_type',
            'booking_reference', 'amount', 'currency', 'payment_method',
            'status', 'card_last_four', 'is_demo_simulation', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'is_demo_simulation', 'created_at']
