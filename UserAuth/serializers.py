"""
Serializers for UserAuth app
Handles user registration, authentication, and profile management
"""

from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from .models import User, EmailVerificationToken, PasswordResetToken
from .utils import (
    validate_unique_email,
    validate_password_confirmation,
    validate_google_token,
    register_social_user,
)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with all validation logic"""

    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    password_confirm = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "uid",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_type",
            "phone_number",
        ]
        extra_kwargs = {"uid": {"read_only": True}}

    def validate(self, attrs):
        """Validate email uniqueness and password confirmation"""
        validate_unique_email(attrs.get("email"))
        validate_password_confirmation(
            attrs.get("password"), attrs.get("password_confirm")
        )
        return attrs

    def validate_user_type(self, value):
        """Only allow consumer and organizer during registration"""
        if value not in ["consumer", "organizer"]:
            raise serializers.ValidationError(
                "User type must be either 'consumer' or 'organizer'"
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        """Create user with email verification token"""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        # Create verification token with 24-hour expiry
        expires_at = timezone.now() + timedelta(hours=24)
        verification_token = EmailVerificationToken.objects.create(
            user=user, expires_at=expires_at
        )

        # Send verification email after transaction commits
        transaction.on_commit(
            lambda: self._send_verification_email(
                user.email, str(verification_token.token)
            )
        )

        return user

    def _send_verification_email(self, email, token):
        """Send verification email (called after transaction commits)"""
        from Common.email_utils import send_verification_email

        try:
            send_verification_email(email, token)
        except Exception as e:
            # Log error but don't fail the registration
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to {email}: {str(e)}")


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification with token"""

    token = serializers.UUIDField()

    @transaction.atomic
    def save(self):
        """Verify user email using token"""
        token = self.validated_data["token"]
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")

        if verification_token.expires_at < timezone.now():
            raise serializers.ValidationError("This verification link has expired.")
        if verification_token.is_used:
            raise serializers.ValidationError(
                "This verification link has already been used."
            )

        if verification_token.is_expired():
            raise serializers.ValidationError("This verification link has expired.")

        user = verification_token.user
        user.is_active = True
        user.is_verified = True
        user.save()

        verification_token.is_used = True
        verification_token.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login with email verification check"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate(self, attrs):
        """Validate login credentials and authenticate user"""
        from django.contrib.auth import authenticate

        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password.")

        # Check if email is verified
        if not user.is_verified:
            raise serializers.ValidationError(
                "Please verify your email first. Check your inbox for the verification link."
            )

        # Authenticate user
        user = authenticate(email=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid email or password.")

        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated.")

        attrs["user"] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile data"""

    class Meta:
        model = User
        fields = [
            "uid",
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "user_type",
            "phone_number",
            "is_verified",
            "is_phone_verified",
            "date_joined",
            "auth_provider",
        ]
        read_only_fields = ["uid"]

    def update(self, instance, validated_data):
        """Update user profile"""
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image
        )
        instance.phone_number = validated_data.get(
            "phone_number", instance.phone_number
        )
        instance.save()
        return instance


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate password change"""
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                "New password and confirmation do not match."
            )
        if attrs.get("old_password") == attrs.get("new_password"):
            raise serializers.ValidationError(
                "New password must be different from old password."
            )
        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email"""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if user exists and needs verification"""
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        if user.is_verified:
            raise serializers.ValidationError("Email is already verified.")

        self.context["user"] = user
        return value

    @transaction.atomic
    def save(self):
        """Generate new token and send email"""
        user = self.context["user"]

        # Mark old tokens as used
        EmailVerificationToken.objects.filter(user=user, is_used=False).update(
            is_used=True
        )

        # Create new token
        expires_at = timezone.now() + timedelta(hours=24)
        token = EmailVerificationToken.objects.create(user=user, expires_at=expires_at)

        # Send verification email after transaction commits
        transaction.on_commit(
            lambda: self._send_verification_email(user.email, str(token.token))
        )

        return token

    def _send_verification_email(self, email, token):
        """Send verification email (called after transaction commits)"""
        from Common.email_utils import send_verification_email

        try:
            send_verification_email(email, token)
        except Exception as e:
            # Log error but don't fail the operation
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to {email}: {str(e)}")


class LogoutSerializer(serializers.Serializer):
    """Serializer for logout endpoint"""

    refresh = serializers.CharField(
        required=True, help_text="Refresh token to blacklist"
    )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset via email"""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Validate user exists"""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for setting new password with token"""

    token = serializers.UUIDField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate password and confirmation match"""
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError("Password and confirmation do not match.")

        return attrs

    def validate_token(self, value):
        """Validate token exists and is valid"""
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
            if reset_token.is_used:
                raise serializers.ValidationError(
                    "This password reset link is already used."
                )
            if reset_token.is_expired():
                raise serializers.ValidationError(
                    "This password reset link is invalid or has expired."
                )
            return value
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid password reset token.")

    @transaction.atomic
    def reset_password(self):
        """Reset user password"""
        token = self.validated_data["token"]
        password = self.validated_data["password"]

        try:
            reset_token = PasswordResetToken.objects.select_for_update().get(
                token=token
            )
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid password reset token.")

        if reset_token.is_used:
            raise serializers.ValidationError(
                "This password reset link is already used."
            )
        if reset_token.is_expired():
            raise serializers.ValidationError(
                "This password reset link is invalid or has expired."
            )

        user = reset_token.user
        user.set_password(password)
        user.save()

        reset_token.is_used = True
        reset_token.save()

        return user


class GoogleSignInSerializer(serializers.Serializer):
    """Serializer for Google OAuth sign-in"""

    access_token = serializers.CharField(min_length=6)

    def validate_access_token(self, value):
        """Validate Google token and register/login user"""
        google_user_data = validate_google_token(value)
        email = google_user_data.get("email")
        first_name = google_user_data.get("given_name")
        last_name = (
            google_user_data.get("family_name")
            if google_user_data.get("family_name")
            else ""
        )
        name = f"{first_name} {last_name}"
        profile_image = (
            google_user_data.get("picture") if google_user_data.get("picture") else None
        )
        provider = "google"
        return register_social_user(provider, email, name, profile_image)
