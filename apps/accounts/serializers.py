from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.models import CustomerProfile, TravelAgentProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at']


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'passport_number', 'nationality', 'date_of_birth', 'address', 'emergency_contact', 'emergency_phone']


class TravelAgentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TravelAgentProfile
        fields = ['id', 'user', 'agency_name', 'license_number', 'business_email', 'bio', 'is_verified', 'rating']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=User.Role.choices, default=User.Role.CUSTOMER)
    # Optional agent fields
    agency_name = serializers.CharField(required=False, allow_blank=True)
    license_number = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'phone', 'agency_name', 'license_number']

    def create(self, validated_data):
        agency_name = validated_data.pop('agency_name', '')
        license_number = validated_data.pop('license_number', '')
        password = validated_data.pop('password')
        role = validated_data.get('role', User.Role.CUSTOMER)

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if role == User.Role.CUSTOMER:
            CustomerProfile.objects.create(user=user)
        elif role == User.Role.AGENT:
            TravelAgentProfile.objects.create(
                user=user,
                agency_name=agency_name or f"{user.username} Tours",
                license_number=license_number or f"LIC-{user.id:04d}"
            )

        return user
