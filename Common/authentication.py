"""
Custom authentication classes for cookie-based JWT authentication
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class that reads tokens from cookies
    Falls back to Authorization header if cookie is not present
    """

    def authenticate(self, request):
        # Try to get token from cookie first
        raw_token = request.COOKIES.get("access_token")

        # If no cookie, fall back to Authorization header
        if raw_token is None:
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token


class CookieJWTRefreshAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class for refresh tokens from cookies
    """

    def authenticate(self, request):
        # Try to get refresh token from cookie
        raw_token = request.COOKIES.get("refresh_token")

        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token
