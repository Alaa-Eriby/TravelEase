from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, filters
from apps.destinations.models import Destination, Country, City, Review
from apps.packages.models import TravelPackage, PackageDeparture
from apps.hotels.models import Hotel, HotelRoom
from apps.bookings.models import PackageBooking, HotelBooking, BookingStatus
from apps.accounts.models import User, CustomerProfile, TravelAgentProfile
from apps.payments.models import PaymentRecord
from apps.core.models import ContactMessage, AuditLog, Notification
from apps.core.serializers import ContactMessageSerializer, AuditLogSerializer, NotificationSerializer

def is_admin_check(user):
    return user.is_authenticated and (user.is_administrator() or user.is_superuser)

def is_agent_check(user):
    return user.is_authenticated and (user.is_agent() or user.is_administrator() or user.is_superuser)


# --- 1. Public Pages ---

def home_view(request):
    featured_destinations = Destination.objects.filter(is_featured=True)[:6]
    if not featured_destinations.exists():
        featured_destinations = Destination.objects.all()[:6]

    featured_packages = TravelPackage.objects.filter(is_active=True, is_featured=True).select_related('destination')[:4]
    if not featured_packages.exists():
        featured_packages = TravelPackage.objects.filter(is_active=True)[:4]

    recommended_hotels = Hotel.objects.filter(is_featured=True).select_related('destination')[:4]
    if not recommended_hotels.exists():
        recommended_hotels = Hotel.objects.all()[:4]

    reviews = Review.objects.filter(is_approved=True, rating__gte=4).select_related('user')[:4]
    countries = Country.objects.all()

    # Public aggregate counters (real numbers from database)
    stats = {
        'destinations_count': Destination.objects.count(),
        'packages_count': TravelPackage.objects.filter(is_active=True).count(),
        'hotels_count': Hotel.objects.count(),
        'happy_travelers_count': User.objects.filter(role=User.Role.CUSTOMER).count(),
    }

    return render(request, 'core/home.html', {
        'featured_destinations': featured_destinations,
        'featured_packages': featured_packages,
        'recommended_hotels': recommended_hotels,
        'reviews': reviews,
        'countries': countries,
        'stats': stats,
    })


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()

        if not (name and email and subject and message_text):
            messages.error(request, "Please fill in all contact form fields.")
            return render(request, 'core/contact.html')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message_text
        )

        messages.success(request, "Thank you! Your message has been sent successfully. Our team will contact you shortly.")
        return redirect('core:contact')

    return render(request, 'core/contact.html')


# --- 2. Travel Agent Dashboard ---

@user_passes_test(is_agent_check)
def agent_dashboard_view(request):
    agent = request.user
    packages = TravelPackage.objects.filter(agent=agent).prefetch_related('departures')
    
    # Customer reservations for this agent's packages
    bookings = PackageBooking.objects.filter(departure__package__agent=agent).select_related('departure__package', 'customer').prefetch_related('travelers')
    
    total_revenue = bookings.filter(status=BookingStatus.CONFIRMED).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    total_travelers = sum(b.travelers_count for b in bookings.filter(status=BookingStatus.CONFIRMED))

    return render(request, 'dashboard/agent/index.html', {
        'packages': packages,
        'bookings': bookings,
        'total_revenue': total_revenue,
        'total_travelers': total_travelers,
        'active_packages_count': packages.filter(is_active=True).count(),
    })


@user_passes_test(is_agent_check)
def agent_package_create_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        destination_id = request.POST.get('destination')
        duration_days = int(request.POST.get('duration_days', 5))
        price_per_person = Decimal(request.POST.get('price_per_person', '0.00'))
        description = request.POST.get('description')
        included_services = request.POST.get('included_services')
        excluded_services = request.POST.get('excluded_services', '')
        image_url = request.POST.get('image_url', '')

        pkg = TravelPackage.objects.create(
            title=title,
            agent=request.user,
            destination_id=destination_id,
            duration_days=duration_days,
            price_per_person=price_per_person,
            description=description,
            included_services=included_services,
            excluded_services=excluded_services,
            image_url=image_url
        )

        # Optional initial departure
        dep_date = request.POST.get('departure_date')
        ret_date = request.POST.get('return_date')
        capacity = int(request.POST.get('capacity', 20) or 20)
        if dep_date and ret_date:
            PackageDeparture.objects.create(
                package=pkg,
                departure_date=dep_date,
                return_date=ret_date,
                total_capacity=capacity
            )

        AuditLog.objects.create(
            user=request.user,
            action="PACKAGE_CREATED",
            target_model="TravelPackage",
            target_id=str(pkg.id),
            details=f"Created package {pkg.title}"
        )

        messages.success(request, f"Package '{pkg.title}' published successfully!")
        return redirect('core:agent_dashboard')

    destinations = Destination.objects.all()
    return render(request, 'dashboard/agent/package_form.html', {
        'destinations': destinations,
        'is_edit': False
    })


@user_passes_test(is_agent_check)
def agent_package_edit_view(request, pk):
    pkg = get_object_or_404(TravelPackage, pk=pk, agent=request.user)

    if request.method == 'POST':
        pkg.title = request.POST.get('title', pkg.title)
        pkg.destination_id = request.POST.get('destination', pkg.destination_id)
        pkg.duration_days = int(request.POST.get('duration_days', pkg.duration_days))
        pkg.price_per_person = Decimal(request.POST.get('price_per_person', pkg.price_per_person))
        pkg.description = request.POST.get('description', pkg.description)
        pkg.included_services = request.POST.get('included_services', pkg.included_services)
        pkg.excluded_services = request.POST.get('excluded_services', pkg.excluded_services)
        pkg.image_url = request.POST.get('image_url', pkg.image_url)
        pkg.is_active = 'is_active' in request.POST
        pkg.save()

        messages.success(request, f"Package '{pkg.title}' updated successfully!")
        return redirect('core:agent_dashboard')

    destinations = Destination.objects.all()
    return render(request, 'dashboard/agent/package_form.html', {
        'package': pkg,
        'destinations': destinations,
        'is_edit': True
    })


@user_passes_test(is_agent_check)
def agent_departure_create_view(request, package_id):
    pkg = get_object_or_404(TravelPackage, pk=package_id, agent=request.user)
    if request.method == 'POST':
        dep_date = request.POST.get('departure_date')
        ret_date = request.POST.get('return_date')
        capacity = int(request.POST.get('capacity', 20))
        price_override = request.POST.get('price_override')

        PackageDeparture.objects.create(
            package=pkg,
            departure_date=dep_date,
            return_date=ret_date,
            total_capacity=capacity,
            price_override=Decimal(price_override) if price_override else None
        )
        messages.success(request, f"Added departure date for '{pkg.title}'.")
    return redirect('core:agent_dashboard')


@user_passes_test(is_agent_check)
def agent_update_booking_status_view(request, booking_id):
    booking = get_object_or_404(PackageBooking, pk=booking_id, departure__package__agent=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            if new_status == BookingStatus.CANCELLED and booking.status != BookingStatus.CANCELLED:
                booking.cancel(reason="Cancelled by Travel Agent")
            else:
                booking.status = new_status
                booking.save(update_fields=['status'])
            messages.success(request, f"Reservation {booking.booking_reference} status updated to {new_status}.")
    return redirect('core:agent_dashboard')


# --- 3. Administrator Dashboard ---

@user_passes_test(is_admin_check)
def admin_dashboard_view(request):
    """
    Administrator Dashboard with real database-backed metrics & statistics.
    """
    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_agents = User.objects.filter(role=User.Role.AGENT).count()
    total_destinations = Destination.objects.count()
    total_packages = TravelPackage.objects.count()
    total_hotels = Hotel.objects.count()
    
    total_package_bookings = PackageBooking.objects.count()
    total_hotel_bookings = HotelBooking.objects.count()
    total_reservations = total_package_bookings + total_hotel_bookings

    pending_bookings = (
        PackageBooking.objects.filter(status=BookingStatus.PENDING).count() +
        HotelBooking.objects.filter(status=BookingStatus.PENDING).count()
    )
    confirmed_bookings = (
        PackageBooking.objects.filter(status=BookingStatus.CONFIRMED).count() +
        HotelBooking.objects.filter(status=BookingStatus.CONFIRMED).count()
    )
    cancelled_bookings = (
        PackageBooking.objects.filter(status=BookingStatus.CANCELLED).count() +
        HotelBooking.objects.filter(status=BookingStatus.CANCELLED).count()
    )

    pkg_rev = PackageBooking.objects.filter(status=BookingStatus.CONFIRMED).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    htl_rev = HotelBooking.objects.filter(status=BookingStatus.CONFIRMED).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    total_revenue = pkg_rev + htl_rev

    recent_bookings = PackageBooking.objects.select_related('customer', 'departure__package')[:5]
    recent_hotel_bookings = HotelBooking.objects.select_related('customer', 'room__hotel')[:5]
    recent_audit_logs = AuditLog.objects.select_related('user')[:8]
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'total_customers': total_customers,
        'total_agents': total_agents,
        'total_destinations': total_destinations,
        'total_packages': total_packages,
        'total_hotels': total_hotels,
        'total_reservations': total_reservations,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_hotel_bookings': recent_hotel_bookings,
        'recent_audit_logs': recent_audit_logs,
        'unread_messages': unread_messages,
    }
    return render(request, 'dashboard/admin/index.html', context)


@user_passes_test(is_admin_check)
def admin_users_view(request):
    users = User.objects.all().order_by('-date_joined')
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'dashboard/admin/users.html', {'users': users, 'role_filter': role_filter})


@user_passes_test(is_admin_check)
def admin_bookings_view(request):
    package_bookings = PackageBooking.objects.all().select_related('customer', 'departure__package')
    hotel_bookings = HotelBooking.objects.all().select_related('customer', 'room__hotel')
    return render(request, 'dashboard/admin/bookings.html', {
        'package_bookings': package_bookings,
        'hotel_bookings': hotel_bookings,
    })


@user_passes_test(is_admin_check)
def admin_messages_view(request):
    contact_messages = ContactMessage.objects.all()
    if request.method == 'POST':
        msg_id = request.POST.get('message_id')
        msg = get_object_or_404(ContactMessage, pk=msg_id)
        msg.is_read = True
        msg.save()
        messages.success(request, f"Marked message #{msg.id} as read.")
        return redirect('core:admin_messages')
    return render(request, 'dashboard/admin/messages.html', {'contact_messages': contact_messages})


@user_passes_test(is_admin_check)
def admin_audit_logs_view(request):
    logs = AuditLog.objects.all().select_related('user')[:100]
    return render(request, 'dashboard/admin/audit_logs.html', {'logs': logs})


@user_passes_test(is_admin_check)
def admin_reports_view(request):
    pkg_revenue = PackageBooking.objects.filter(status=BookingStatus.CONFIRMED).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    htl_revenue = HotelBooking.objects.filter(status=BookingStatus.CONFIRMED).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0.00')
    
    top_destinations = Destination.objects.annotate(
        packages_count=Count('packages', distinct=True),
        hotels_count=Count('hotels', distinct=True)
    ).order_by('-packages_count')[:10]

    return render(request, 'dashboard/admin/reports.html', {
        'pkg_revenue': pkg_revenue,
        'htl_revenue': htl_revenue,
        'total_revenue': pkg_revenue + htl_revenue,
        'top_destinations': top_destinations,
    })


# --- REST API ViewSets ---

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().select_related('user')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
