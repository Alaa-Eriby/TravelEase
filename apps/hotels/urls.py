from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.hotels import views

app_name = 'hotels'

router = DefaultRouter()
router.register(r'api/hotels', views.HotelViewSet, basename='api_hotels')
router.register(r'api/rooms', views.HotelRoomViewSet, basename='api_rooms')

urlpatterns = [
    path('', views.hotel_list_view, name='list'),
    path('<int:pk>/', views.hotel_detail_view, name='detail'),
    path('rooms/<int:room_id>/book/', views.hotel_booking_view, name='booking'),
    path('', include(router.urls)),
]
