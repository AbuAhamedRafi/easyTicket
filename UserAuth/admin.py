from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, EmailVerificationToken, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""

    list_display = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_verified",
        "is_active",
        "date_joined",
    ]
    list_filter = [
        "user_type",
        "is_verified",
        "is_active",
        "auth_provider",
        "date_joined",
    ]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal Info",
            {"fields": ("first_name", "last_name", "phone_number", "profile_image")},
        ),
        ("User Type & Provider", {"fields": ("user_type", "auth_provider")}),
        ("Verification Status", {"fields": ("is_verified", "is_phone_verified")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "user_type",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    readonly_fields = ["date_joined", "last_login"]


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin for Email Verification Tokens"""

    list_display = ["user", "token", "created_at", "expires_at", "is_used"]
    list_filter = ["is_used", "created_at", "expires_at"]
    search_fields = ["user__email", "token"]
    readonly_fields = ["token", "created_at", "expires_at"]
    ordering = ["-created_at"]


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin for Password Reset Tokens"""

    list_display = ["user", "token", "created_at", "expires_at", "is_used"]
    list_filter = ["is_used", "created_at", "expires_at"]
    search_fields = ["user__email", "token"]
    readonly_fields = ["token", "created_at", "expires_at"]
    ordering = ["-created_at"]
