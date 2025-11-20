"""
Utility functions for UserAuth app
Handles validation, social authentication, and token generation
"""

import random
import requests
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

# Optional Google OAuth imports
try:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    google_requests = None
    id_token = None


def validate_unique_email(email, exclude_uid=None):
    """
    Validate that email is unique in the database

    Args:
        email (str): Email address to validate
        exclude_uid (UUID, optional): UID to exclude from check (for updates)

    Returns:
        str: Validated email address

    Raises:
        ValidationError: If email already exists
    """
    queryset = User.objects.filter(email=email)
    if exclude_uid:
        queryset = queryset.exclude(uid=exclude_uid)

    if queryset.exists():
        raise serializers.ValidationError("User with this email already exists.")
    return email


def validate_password_confirmation(password, password_confirm):
    """
    Validate that password meets requirements and matches confirmation

    Args:
        password (str): Password
        password_confirm (str): Password confirmation

    Returns:
        str: Validated password

    Raises:
        ValidationError: If passwords don't match or don't meet requirements
    """
    if password and len(password) < 8:
        raise serializers.ValidationError(
            "Password must be at least 8 characters long."
        )
    if password != password_confirm:
        raise serializers.ValidationError("Passwords don't match.")
    return password


def validate_google_token(token):
    """
    Validate Google OAuth token and return user info

    Args:
        token (str): Google OAuth access token

    Returns:
        dict: User information from Google

    Raises:
        ValidationError: If token is invalid or Google auth not available
    """
    if not GOOGLE_AUTH_AVAILABLE:
        raise serializers.ValidationError(
            "Google authentication is not available. Please install google-auth packages."
        )

    GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)
    if not GOOGLE_CLIENT_ID:
        raise serializers.ValidationError("Google authentication is not configured.")

    try:
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        if "accounts.google.com" not in id_info["iss"]:
            raise ValueError("Wrong issuer.")
        return id_info
    except ValueError:
        raise serializers.ValidationError("Invalid Google token.")


def social_login_user_data(user):
    """
    Generate JWT tokens and user data for social login

    Args:
        user (User): User instance

    Returns:
        dict: Access token, refresh token, and user data
    """
    social_password = getattr(
        settings, "SOCIAL_AUTH_PASSWORD", "default_social_password_change_in_production"
    )
    user = authenticate(email=user.email, password=social_password)
    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": {
            "uid": str(user.uid),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "user_type": user.user_type,
            "is_verified": user.is_verified,
            "auth_provider": user.auth_provider,
        },
    }


def register_social_user(provider, email, name=None, profile_image=None):
    """
    Register or login user via social authentication

    Args:
        provider (str): Auth provider ('google', 'facebook', etc.)
        email (str): User's email from social provider
        name (str, optional): User's full name
        profile_image (str, optional): Profile image URL

    Returns:
        dict: User data with JWT tokens

    Raises:
        ValidationError: If user exists with different provider
    """
    user = User.objects.filter(email=email).first()

    if user:
        # User exists - check if provider matches
        if user.auth_provider != provider:
            raise serializers.ValidationError(
                f"Please login with {user.auth_provider}."
            )
        return social_login_user_data(user)
    else:
        # Create new user
        # Generate username from name or random
        if not name:
            username = f"User{random.randint(1000, 9999)}"
            first_name = username
            last_name = ""
        else:
            # Split name into first and last
            name_parts = name.strip().split()
            first_name = name_parts[0] if name_parts else "User"
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

        # Download profile image if provided
        image_content = None
        if profile_image:
            try:
                response = requests.get(profile_image, stream=True, timeout=10)
                response.raise_for_status()
                image_content = ContentFile(response.content)
            except requests.exceptions.RequestException as e:
                # Log error but don't fail registration
                print(f"Error downloading profile image: {e}")
                profile_image = None

        # Create user
        user = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_verified=True,
            auth_provider=provider,
            user_type="consumer",
        )

        # Save profile image if downloaded
        if image_content:
            user.profile_image.save(f"{user.uid}_profile.jpg", image_content)

        # Set social auth password
        social_password = getattr(
            settings,
            "SOCIAL_AUTH_PASSWORD",
            "default_social_password_change_in_production",
        )
        user.set_password(social_password)
        user.save()

        return social_login_user_data(user)


def generate_unique_order_number(prefix="OE"):
    """
    Generate a unique order number with format: PREFIX-YYYYMMDD-XXXX

    Args:
        prefix (str): Prefix for order number (default: "OE" for EasyTicket)

    Returns:
        str: Unique order number
    """
    from datetime import datetime
    from Orders.models import Order

    date_str = datetime.now().strftime("%Y%m%d")

    # Find the last order of the day
    today_orders = Order.objects.filter(
        order_number__startswith=f"{prefix}-{date_str}"
    ).count()

    sequence = today_orders + 1
    order_number = f"{prefix}-{date_str}-{sequence:04d}"

    return order_number
