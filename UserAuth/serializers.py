from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import User
from Common.email_utils import send_verification_email, send_welcome_email


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with all validation logic"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
        ]
        read_only_fields = ["id"]

    def validate_user_type(self, value):
        """Only allow consumer and organizer during registration"""
        if value not in ["consumer", "organizer"]:
            raise serializers.ValidationError(
                "User type must be either 'consumer' or 'organizer'"
            )
        return value

    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match"}
            )
        return attrs

    def create(self, validated_data):
        """Create user with email verification token"""
        # Remove password_confirm from validated data
        validated_data.pop("password_confirm")

        # Extract password
        password = validated_data.pop("password")

        # Generate email verification token
        verification_token = str(uuid.uuid4())

        # Create user
        user = User.objects.create_user(
            password=password,
            email_verification_token=verification_token,
            email_verification_token_created=timezone.now(),
            is_email_verified=False,
            **validated_data
        )

        # Send verification email
        send_verification_email(user.email, verification_token)

        return user


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification with token"""

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Validate token exists and not expired"""
        try:
            user = User.objects.get(email_verification_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token")

        # Check if already verified
        if user.is_email_verified:
            raise serializers.ValidationError("Email already verified")

        # Check token expiry (24 hours)
        if user.email_verification_token_created:
            expiry_time = user.email_verification_token_created + timedelta(hours=24)
            if timezone.now() > expiry_time:
                raise serializers.ValidationError("Verification token has expired")

        # Store user in context for use in view
        self.context["user"] = user
        return value

    def save(self):
        """Mark email as verified and send welcome email"""
        user = self.context["user"]
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_token_created = None
        user.save(
            update_fields=[
                "is_email_verified",
                "email_verification_token",
                "email_verification_token_created",
            ]
        )

        # Send welcome email after successful verification
        user_name = user.first_name or user.email.split("@")[0]
        send_welcome_email(user.email, user_name)

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with email verification check"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Authenticate user and check email verification"""
        email = attrs.get("email")
        password = attrs.get("password")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "No account found with this email"}
            )

        # Check if email is verified
        if not user.is_email_verified:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Please verify your email first. Check your inbox for the verification link or request a new one."
                    ]
                }
            )

        # Authenticate user
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError({"password": "Invalid password"})

        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError(
                {"email": "This account has been deactivated"}
            )

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
            "auth_provider",
        ]
        read_only_fields = [
            "id",
            "email",
            "user_type",
            "is_email_verified",
            "is_phone_verified",
            "date_joined",
            "auth_provider",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate_old_password(self, value):
        """Verify old password is correct"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value

    def validate(self, attrs):
        """Validate new passwords match"""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match"}
            )
        return attrs

    def save(self):
        """Update user password"""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if user exists and needs verification"""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email")

        if user.is_email_verified:
            raise serializers.ValidationError("Email is already verified")

        self.context["user"] = user
        return value

    def save(self):
        """Generate new token and send verification email"""
        user = self.context["user"]
        user.email_verification_token = str(uuid.uuid4())
        user.email_verification_token_created = timezone.now()
        user.save(
            update_fields=[
                "email_verification_token",
                "email_verification_token_created",
            ]
        )

        # Send verification email
        send_verification_email(user.email, user.email_verification_token)

        return user


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint"""

    refresh = serializers.CharField(
        required=True, help_text="Refresh token to blacklist"
    )
