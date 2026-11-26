from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.payments import views

app_name = 'payments'

router = DefaultRouter()
router.register(r'api/records', views.PaymentRecordViewSet, basename='api_payments')

urlpatterns = [
    path('', include(router.urls)),
]
