"""
Custom throttling classes for rate limiting
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthThrottle(AnonRateThrottle):
    """
    Rate limit for authentication endpoints (login, registration)
    Prevents brute force attacks
    """

    scope = "auth"


class PaymentThrottle(UserRateThrottle):
    """
    Rate limit for payment creation endpoints
    Prevents abuse of payment system
    """

    scope = "payment"
