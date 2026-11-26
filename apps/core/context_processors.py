from apps.core.models import Notification

def global_context(request):
    unread_notifications_count = 0
    recent_notifications = []
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(recipient=request.user)[:5]
    
    return {
        'APP_NAME': 'TravelEase',
        'APP_TAGLINE': 'Smart Travel and Tourism Booking System',
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
    }
