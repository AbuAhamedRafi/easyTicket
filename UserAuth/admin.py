from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model"""

    list_display = [
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_email_verified",
        "is_active",
        "date_joined",
    ]
    list_filter = [
        "user_type",
        "is_email_verified",
        "is_active",
        "auth_provider",
        "date_joined",
    ]
    search_fields = ["email", "first_name", "last_name", "phone_number"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone_number")}),
        ("User Type & Provider", {"fields": ("user_type", "auth_provider")}),
        ("Verification Status", {"fields": ("is_email_verified", "is_phone_verified")}),
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
