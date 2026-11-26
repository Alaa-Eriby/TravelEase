from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.models import User, CustomerProfile, TravelAgentProfile
from apps.accounts.serializers import UserSerializer, CustomerProfileSerializer, TravelAgentProfileSerializer, RegisterSerializer
from apps.core.models import AuditLog

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        role = request.POST.get('role', User.Role.CUSTOMER)
        agency_name = request.POST.get('agency_name', '')
        license_number = request.POST.get('license_number', '')

        if password != password_confirm:
            messages.error(request, "Passwords do not match!")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            role=role
        )

        if role == User.Role.CUSTOMER:
            CustomerProfile.objects.create(user=user)
        elif role == User.Role.AGENT:
            TravelAgentProfile.objects.create(
                user=user,
                agency_name=agency_name or f"{user.username} Travel",
                license_number=license_number or f"LIC-{user.id:04d}"
            )

        AuditLog.objects.create(
            user=user,
            action="USER_REGISTERED",
            target_model="User",
            target_id=str(user.id),
            details=f"Registered with role {user.get_role_display()}"
        )

        login(request, user)
        messages.success(request, f"Welcome to TravelEase, {user.first_name or user.username}!")
        return redirect('accounts:dashboard_redirect')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            AuditLog.objects.create(
                user=user,
                action="USER_LOGIN",
                target_model="User",
                target_id=str(user.id),
                details="Logged in via web interface"
            )
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user,
            action="USER_LOGOUT",
            target_model="User",
            target_id=str(request.user.id),
            details="Logged out"
        )
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('core:home')


@login_required
def dashboard_redirect_view(request):
    """
    Intelligently routes the user to their designated dashboard based on role:
    - Customer -> Customer Dashboard
    - Agent -> Agent Dashboard
    - Administrator -> Admin Panel
    """
    if request.user.is_administrator():
        return redirect('core:admin_dashboard')
    elif request.user.is_agent():
        return redirect('core:agent_dashboard')
    else:
        return redirect('bookings:customer_dashboard')


@login_required
def profile_view(request):
    user = request.user
    customer_profile = getattr(user, 'customer_profile', None)
    agent_profile = getattr(user, 'agent_profile', None)

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone = request.POST.get('phone', user.phone)
        user.save()

        if customer_profile:
            customer_profile.passport_number = request.POST.get('passport_number', customer_profile.passport_number)
            customer_profile.nationality = request.POST.get('nationality', customer_profile.nationality)
            customer_profile.address = request.POST.get('address', customer_profile.address)
            customer_profile.emergency_contact = request.POST.get('emergency_contact', customer_profile.emergency_contact)
            customer_profile.emergency_phone = request.POST.get('emergency_phone', customer_profile.emergency_phone)
            customer_profile.save()

        if agent_profile:
            agent_profile.agency_name = request.POST.get('agency_name', agent_profile.agency_name)
            agent_profile.bio = request.POST.get('bio', agent_profile.bio)
            agent_profile.business_email = request.POST.get('business_email', agent_profile.business_email)
            agent_profile.save()

        AuditLog.objects.create(
            user=user,
            action="PROFILE_UPDATED",
            target_model="User",
            target_id=str(user.id),
            details="User updated personal profile"
        )

        messages.success(request, "Profile updated successfully!")
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'customer_profile': customer_profile,
        'agent_profile': agent_profile
    })


# --- REST API Views ---

class RegisterAPIView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
