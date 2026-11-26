from django.urls import path
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),

    # REST APIs
    path('api/register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
]
