"""
Payment-related URL patterns
"""

from django.urls import path
from .payment_views import (
    PaymentIntentView,
    ConfirmPaymentView,
    RefundView,
    PaymentStatusView,
)
from .webhooks import stripe_webhook

urlpatterns = [
    # Payment Intent
    path(
        "orders/<uuid:order_id>/create-payment-intent/",
        PaymentIntentView.as_view(),
        name="create-payment-intent",
    ),
    # Confirm Payment
    path(
        "orders/<uuid:order_id>/confirm-payment/",
        ConfirmPaymentView.as_view(),
        name="confirm-payment",
    ),
    # Payment Status
    path(
        "orders/<uuid:order_id>/payment-status/",
        PaymentStatusView.as_view(),
        name="payment-status",
    ),
    # Refund
    path("orders/<uuid:order_id>/refund/", RefundView.as_view(), name="refund-order"),
    # Stripe Webhook
    path("payments/webhook/", stripe_webhook, name="stripe-webhook"),
]
