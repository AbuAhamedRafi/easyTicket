"""
Stripe Webhook Handlers
Processes Stripe webhook events
"""

import stripe
import json
import logging
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils import timezone

from .models import Order

# Stripe webhook secret
WEBHOOK_SECRET = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

# Setup logger
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle incoming Stripe webhooks with signature verification
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    # Enforce webhook signature verification
    if not WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET not configured - webhook rejected")
        return JsonResponse(
            {
                "error": "Webhook secret not configured. Please set STRIPE_WEBHOOK_SECRET in environment variables."
            },
            status=500,
        )

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid webhook payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid webhook signature: {e}")
        return HttpResponse(status=400)

    # Get event ID and type
    event_id = event.get("id")
    event_type = event.get("type")

    # Check for idempotency - prevent duplicate processing
    from .models import WebhookEvent

    if WebhookEvent.objects.filter(event_id=event_id).exists():
        logger.info(f"Webhook event {event_id} already processed, skipping")
        return HttpResponse(status=200)

    # Record the event as processed
    try:
        WebhookEvent.objects.create(
            event_id=event_id, event_type=event_type, payload=event
        )
    except Exception as e:
        logger.error(f"Failed to record webhook event {event_id}: {e}")
        # Continue processing even if recording fails

    # Handle the event
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
        logger.info(f"Unhandled event type: {event_type}")

    return HttpResponse(status=200)


def handle_payment_succeeded(event):
    """Handle successful payment"""
    payment_intent = event["data"]["object"]
    payment_intent_id = payment_intent["id"]

    # Get order from metadata
    order_id = payment_intent.get("metadata", {}).get("order_id")
    if not order_id:
        logger.error(f"No order_id in payment intent {payment_intent_id}")
        return HttpResponse(status=400)

    try:
        order = Order.objects.get(id=order_id)

        # Check if order has expired
        if order.is_expired:
            logger.warning(f"Payment received for expired order {order.order_number}")
            # Initiate refund for expired order
            try:
                stripe.Refund.create(payment_intent=payment_intent_id)
                order.status = "refunded"
                order.cancellation_reason = "Order expired before payment was completed"
                order.save(update_fields=["status", "cancellation_reason"])
                logger.info(f"Refund initiated for expired order {order.order_number}")
            except Exception as e:
                logger.error(
                    f"Failed to refund expired order {order.order_number}: {e}"
                )
            return HttpResponse(status=200)

        # Update order status if not already confirmed
        if order.status != "confirmed":
            try:
                with transaction.atomic():
                    order.status = "confirmed"
                    order.payment_id = payment_intent_id
                    order.paid_at = timezone.now()
                    order.save(update_fields=["status", "payment_id", "paid_at"])

                    logger.info(f"Order {order.order_number} confirmed via webhook")

                # Send confirmation email (outside transaction to avoid blocking)
                try:
                    from Common.email_utils import send_order_confirmation_email

                    send_order_confirmation_email(order)
                    logger.info(
                        f"Confirmation email sent for order {order.order_number}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to send confirmation email for order {order.order_number}: {e}"
                    )
                    # Don't fail the webhook if email fails

            except Exception as e:
                logger.error(f"Failed to confirm order {order.order_number}: {e}")
                return HttpResponse(status=500)  # Stripe will retry

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        logger.error(
            f"Order {order_id} not found for payment intent {payment_intent_id}"
        )
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

        logger.info(f"Order {order.order_number} refunded via webhook")

        # Send refund notification email
        try:
            from Common.email_utils import send_order_cancelled_email

            send_order_cancelled_email(order)
            logger.info(
                f"Refund notification email sent for order {order.order_number}"
            )
        except Exception as e:
            logger.error(
                f"Failed to send refund email for order {order.order_number}: {e}"
            )

        return HttpResponse(status=200)

    except Order.DoesNotExist:
        logger.warning(f"Order not found for payment intent {payment_intent_id}")
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
