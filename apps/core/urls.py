from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core import views

app_name = 'core'

router = DefaultRouter()
router.register(r'api/contact', views.ContactMessageViewSet, basename='api_contact')
router.register(r'api/audit-logs', views.AuditLogViewSet, basename='api_audit_logs')
router.register(r'api/notifications', views.NotificationViewSet, basename='api_notifications')

urlpatterns = [
    # Public Pages
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Travel Agent Dashboard
    path('agent/dashboard/', views.agent_dashboard_view, name='agent_dashboard'),
    path('agent/packages/create/', views.agent_package_create_view, name='agent_package_create'),
    path('agent/packages/<int:pk>/edit/', views.agent_package_edit_view, name='agent_package_edit'),
    path('agent/packages/<int:package_id>/departures/create/', views.agent_departure_create_view, name='agent_departure_create'),
    path('agent/bookings/<int:booking_id>/status/', views.agent_update_booking_status_view, name='agent_update_booking_status'),

    # Administrator Dashboard
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/bookings/', views.admin_bookings_view, name='admin_bookings'),
    path('admin-panel/messages/', views.admin_messages_view, name='admin_messages'),
    path('admin-panel/audit-logs/', views.admin_audit_logs_view, name='admin_audit_logs'),
    path('admin-panel/reports/', views.admin_reports_view, name='admin_reports'),

    # APIs
    path('', include(router.urls)),
]
