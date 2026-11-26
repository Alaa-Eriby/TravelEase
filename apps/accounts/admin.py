from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.accounts.models import User, CustomerProfile, TravelAgentProfile

class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False

class TravelAgentProfileInline(admin.StackedInline):
    model = TravelAgentProfile
    can_delete = False

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('TravelEase Custom Fields', {'fields': ('role', 'phone', 'avatar')}),
    )
    inlines = [CustomerProfileInline, TravelAgentProfileInline]

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'passport_number', 'nationality')
    search_fields = ('user__username', 'passport_number', 'nationality')

@admin.register(TravelAgentProfile)
class TravelAgentProfileAdmin(admin.ModelAdmin):
    list_display = ('agency_name', 'user', 'license_number', 'is_verified', 'rating')
    list_filter = ('is_verified',)
    search_fields = ('agency_name', 'license_number', 'user__username')
