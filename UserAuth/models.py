"""
User models for EasyTicket authentication system
"""
import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from Common.models import BaseModelWithUID


def user_media_file_prefix(instance, filename):
    """Generate file path for user profile pictures"""
    return f"users/profile_pictures/{instance.uid}/media/{filename}"


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password"""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with admin privileges"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("user_type", "admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, BaseModelWithUID):
    """Custom User model with email as the primary identifier"""

    USER_TYPE_CHOICES = [
        ("consumer", "Consumer"),
        ("organizer", "Organizer"),
        ("admin", "Admin"),
    ]

    AUTH_PROVIDER_CHOICES = [
        ("email", "Email"),
        ("google", "Google"),
        ("facebook", "Facebook"),
    ]

    # Primary fields
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True)

    # User information
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    profile_image = models.ImageField(
        upload_to=user_media_file_prefix,
        null=True,
        blank=True,
        help_text="User profile picture"
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="consumer"
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AUTH_PROVIDER_CHOICES,
        default="email"
    )

    # Verification and status fields
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )
    is_phone_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Manager
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def get_short_name(self):
        """Return the user's short name"""
        return self.first_name or self.email

    @property
    def is_consumer(self):
        """Check if user is a consumer"""
        return self.user_type == "consumer"

    @property
    def is_organizer(self):
        """Check if user is an organizer"""
        return self.user_type == "organizer"

    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.user_type == "admin" or self.is_superuser


class EmailVerificationToken(models.Model):
    """Token for email verification"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="verification_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Verification token for {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Email Verification Token"
        verbose_name_plural = "Email Verification Tokens"


class PasswordResetToken(models.Model):
    """Token for password reset"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if token has expired"""
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
