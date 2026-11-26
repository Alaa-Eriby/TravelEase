from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.bookings import views

app_name = 'bookings'

router = DefaultRouter()
router.register(r'api/package-bookings', views.PackageBookingViewSet, basename='api_package_bookings')
router.register(r'api/hotel-bookings', views.HotelBookingViewSet, basename='api_hotel_bookings')

urlpatterns = [
    path('dashboard/', views.customer_dashboard_view, name='customer_dashboard'),
    path('package/confirmation/<str:booking_reference>/', views.package_confirmation_view, name='package_confirmation'),
    path('hotel/confirmation/<str:booking_reference>/', views.hotel_confirmation_view, name='hotel_confirmation'),
    path('package/<int:pk>/cancel/', views.cancel_package_booking_view, name='cancel_package_booking'),
    path('hotel/<int:pk>/cancel/', views.cancel_hotel_booking_view, name='cancel_hotel_booking'),
    path('', include(router.urls)),
]
