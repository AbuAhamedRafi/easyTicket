"""
Stripe Payment Service
Handles all Stripe payment operations
"""

import stripe
from decimal import Decimal
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Order

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePaymentService:
    """Service class for Stripe payment operations"""

    @staticmethod
    def calculate_service_fee(subtotal: Decimal) -> Decimal:
        """
        Calculate platform service fee
        Default: 5% of subtotal
        """
        fee_percentage = Decimal(
            str(getattr(settings, "STRIPE_SERVICE_FEE_PERCENTAGE", 5.0))
        )
        return (subtotal * fee_percentage / Decimal("100")).quantize(Decimal("0.01"))

    @staticmethod
    def calculate_total_amount(order: Order) -> Decimal:
        """Calculate total amount including service fee"""
        service_fee = StripePaymentService.calculate_service_fee(order.subtotal)
        total = order.subtotal + service_fee - order.discount_amount
        return max(Decimal("0.00"), total)

    @staticmethod
    def create_payment_intent(order: Order) -> dict:
        """
        Create a Stripe PaymentIntent for an order

        Args:
            order: Order instance

        Returns:
            dict with payment_intent data
        """
        # Calculate amounts
        service_fee = StripePaymentService.calculate_service_fee(order.subtotal)
        total_amount = StripePaymentService.calculate_total_amount(order)

        # Update order with calculated fees
        order.service_fee = service_fee
        order.total_amount = total_amount
        order.save(update_fields=["service_fee", "total_amount"])

        # Convert to cents (Stripe uses smallest currency unit)
        amount_cents = int(total_amount * Decimal("100"))

        try:
            # Create PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=order.currency.lower(),
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "event_id": str(order.event.id),
                    "user_id": str(order.user.id),
                },
                description=f"Order {order.order_number} - {order.event.title}",
                receipt_email=order.buyer_email or order.user.email,
                automatic_payment_methods={
                    "enabled": True,
                },
            )

            # Store payment ID in order
            order.payment_id = payment_intent.id
            order.payment_method = "stripe"
            order.status = "processing"
            order.save(update_fields=["payment_id", "payment_method", "status"])

            return {
                "client_secret": payment_intent.client_secret,
                "payment_intent_id": payment_intent.id,
                "amount": amount_cents,
                "currency": order.currency.lower(),
                "status": payment_intent.status,
            }

        except stripe.error.StripeError as e:
            # Handle Stripe errors
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def confirm_payment(order: Order, payment_intent_id: str) -> bool:
        """
        Confirm a payment and update order status

        Args:
            order: Order instance
            payment_intent_id: Stripe PaymentIntent ID

        Returns:
            bool: Success status
        """
        try:
            # Retrieve the PaymentIntent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Verify it belongs to this order
            if payment_intent.metadata.get("order_id") != str(order.id):
                raise ValueError("Payment intent does not match order")

            # Check payment status
            if payment_intent.status == "succeeded":
                with transaction.atomic():
                    # Update order status
                    order.status = "confirmed"
                    order.payment_id = payment_intent_id
                    order.paid_at = timezone.now()
                    order.save(update_fields=["status", "payment_id", "paid_at"])

                return True
            else:
                # Payment not successful
                order.status = "failed"
                order.save(update_fields=["status"])
                return False

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def create_refund(order: Order, amount: Decimal = None, reason: str = None) -> dict:
        """
        Create a refund for an order

        Args:
            order: Order instance
            amount: Amount to refund (None for full refund)
            reason: Refund reason

        Returns:
            dict with refund data
        """
        if not order.payment_id:
            raise ValueError("Order has no associated payment")

        if order.status not in ["confirmed"]:
            raise ValueError("Order must be confirmed to refund")

        try:
            # Prepare refund parameters
            refund_params = {
                "payment_intent": order.payment_id,
            }

            # Partial refund if amount specified
            if amount:
                refund_params["amount"] = int(
                    amount * Decimal("100")
                )  # Convert to cents

            # Add reason if provided
            if reason:
                refund_params["reason"] = reason

            # Create refund in Stripe
            refund = stripe.Refund.create(**refund_params)

            # Update order status
            with transaction.atomic():
                order.status = "refunded"
                order.save(update_fields=["status"])

            return {
                "refund_id": refund.id,
                "amount": refund.amount / 100,  # Convert back to dollars
                "currency": refund.currency,
                "status": refund.status,
            }

        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")

    @staticmethod
    def retrieve_payment_intent(payment_intent_id: str) -> dict:
        """Retrieve PaymentIntent details from Stripe"""
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": payment_intent.id,
                "amount": payment_intent.amount / 100,
                "currency": payment_intent.currency,
                "status": payment_intent.status,
                "metadata": payment_intent.metadata,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Stripe error: {str(e)}")
