from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.destinations import views

app_name = 'destinations'

router = DefaultRouter()
router.register(r'api/countries', views.CountryViewSet, basename='api_countries')
router.register(r'api/cities', views.CityViewSet, basename='api_cities')
router.register(r'api/destinations', views.DestinationViewSet, basename='api_destinations')
router.register(r'api/reviews', views.ReviewViewSet, basename='api_reviews')
router.register(r'api/favorites', views.FavoriteDestinationViewSet, basename='api_favorites')

urlpatterns = [
    path('', views.destination_list_view, name='list'),
    path('<int:pk>/', views.destination_detail_view, name='detail'),
    path('<int:pk>/favorite/', views.toggle_favorite_view, name='toggle_favorite'),
    path('<int:pk>/review/', views.add_review_view, name='add_review'),
    path('', include(router.urls)),
]
