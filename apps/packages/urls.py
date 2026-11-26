from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.packages import views

app_name = 'packages'

router = DefaultRouter()
router.register(r'api/packages', views.TravelPackageViewSet, basename='api_packages')
router.register(r'api/departures', views.PackageDepartureViewSet, basename='api_departures')

urlpatterns = [
    path('', views.package_list_view, name='list'),
    path('<int:pk>/', views.package_detail_view, name='detail'),
    path('<int:pk>/book/', views.package_booking_wizard_view, name='booking_wizard'),
    path('', include(router.urls)),
]
