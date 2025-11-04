"""
Stripe Webhook Handlers
Processes Stripe webhook events
"""

import stripe
import json
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone

from .models import Order

# Stripe webhook secret
WEBHOOK_SECRET = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle incoming Stripe webhooks
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    # Verify webhook signature (if secret is configured)
    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
        except ValueError:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            return HttpResponse(status=400)
    else:
        # No verification in development
        try:
            event = json.loads(payload)
        except json.JSONDecodeError:
            return HttpResponse(status=400)

    # Handle the event
    event_type = event["type"]

    if event_type == "payment_intent.succeeded":
        return handle_payment_succeeded(event)
    elif event_type == "payment_intent.payment_failed":
        return handle_payment_failed(event)
    elif event_type == "charge.refunded":
        return handle_refund(event)
    elif event_type == "payment_intent.canceled":
        return handle_payment_canceled(event)
    else:
        # Unhandled event type
        print(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)


def handle_payment_succeeded(event):
    """Handle successful payment"""
    payment_intent = event["data"]["object"]
    payment_intent_id = payment_intent["id"]

    # Get order from metadata
    order_id = payment_intent.get("metadata", {}).get("order_id")
    if not order_id:
        print(f"No order_id in payment intent {payment_intent_id}")
        return HttpResponse(status=400)

    try:
        order = Order.objects.get(id=order_id)

        # Update order status if not already confirmed
        if order.status != "confirmed":
            with transaction.atomic():
                order.status = "confirmed"
                order.payment_id = payment_intent_id
                order.paid_at = timezone.now()
                order.save(update_fields=["status", "payment_id", "paid_at"])

                print(f"Order {order.order_number} confirmed via webhook")

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        print(f"Order {order_id} not found for payment intent {payment_intent_id}")
        return HttpResponse(status=404)


def handle_payment_failed(event):
    """Handle failed payment"""
    payment_intent = event["data"]["object"]
    payment_intent_id = payment_intent["id"]

    # Get order from metadata
    order_id = payment_intent.get("metadata", {}).get("order_id")
    if not order_id:
        return HttpResponse(status=400)

    try:
        order = Order.objects.get(id=order_id)

        # Update order status
        order.status = "failed"
        order.save(update_fields=["status"])

        print(f"Order {order.order_number} payment failed via webhook")

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        return HttpResponse(status=404)


def handle_refund(event):
    """Handle refund"""
    charge = event["data"]["object"]
    payment_intent_id = charge.get("payment_intent")

    if not payment_intent_id:
        return HttpResponse(status=200)

    try:
        order = Order.objects.get(payment_id=payment_intent_id)

        # Update order status
        order.status = "refunded"
        order.save(update_fields=["status"])

        print(f"Order {order.order_number} refunded via webhook")

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        print(f"Order not found for payment intent {payment_intent_id}")
        return HttpResponse(status=200)


def handle_payment_canceled(event):
    """Handle canceled payment"""
    payment_intent = event["data"]["object"]

    # Get order from metadata
    order_id = payment_intent.get("metadata", {}).get("order_id")
    if not order_id:
        return HttpResponse(status=200)

    try:
        order = Order.objects.get(id=order_id)

        # Update order status
        if order.status == "processing":
            order.status = "cancelled"
            order.save(update_fields=["status"])

            print(f"Order {order.order_number} cancelled via webhook")

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        return HttpResponse(status=200)
