"""
Webhook URL Configuration
Separate webhook URLs for better organization
"""

from django.urls import path
from .webhooks import stripe_webhook

urlpatterns = [
    path("stripe/", stripe_webhook, name="stripe-webhook"),
]
