from rest_framework import viewsets, permissions
from apps.payments.models import PaymentRecord
from apps.payments.serializers import PaymentRecordSerializer

class PaymentRecordViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_administrator():
            return PaymentRecord.objects.all().select_related('user')
        return PaymentRecord.objects.filter(user=user)
