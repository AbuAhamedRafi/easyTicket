"""
Views for Orders app
Handles all order and payment operations
"""

import stripe
import logging
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from Common.throttling import PaymentThrottle

from .models import Order, OrderItem
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
    OrderCancelSerializer,
    OrderConfirmPaymentSerializer,
    OrderItemSerializer,
)
from .permissions import IsOrderOwner, IsOrderOwnerOrAdmin

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List user's orders",
        description="Get all orders for the authenticated user",
        tags=["Orders"],
    ),
    retrieve=extend_schema(
        summary="Get order details",
        description="Get detailed information about a specific order",
        tags=["Orders"],
    ),
    create=extend_schema(
        summary="Create new order",
        description="Create a new order with ticket items",
        tags=["Orders"],
    ),
)
class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders

    list: Get all orders for the authenticated user
    retrieve: Get details of a specific order
    create: Create a new order
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get orders for current user (or all for admins)"""
        user = self.request.user

        if user.is_staff:
            # Admins can see all orders
            return Order.objects.select_related("user", "event").prefetch_related(
                "items"
            )

        # Regular users see only their orders
        return (
            Order.objects.filter(user=user)
            .select_related("event")
            .prefetch_related("items")
        )

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "create":
            return OrderCreateSerializer
        elif self.action == "cancel":
            return OrderCancelSerializer
        elif self.action == "confirm_payment":
            return OrderConfirmPaymentSerializer
        return OrderDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["retrieve", "cancel"]:
            return [IsAuthenticated(), IsOrderOwner()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """Create order and return detailed response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Return detailed order information
        detail_serializer = OrderDetailSerializer(order)
        headers = self.get_success_headers(detail_serializer.data)
        return Response(
            detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @extend_schema(
        summary="Get pending orders",
        description="Get all pending orders for the authenticated user",
        tags=["Orders"],
    )
    @action(detail=False, methods=["get"])
    def pending(self, request):
        """Get pending orders"""
        orders = self.get_queryset().filter(status="pending")
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get confirmed orders",
        description="Get all confirmed (paid) orders for the authenticated user",
        tags=["Orders"],
    )
    @action(detail=False, methods=["get"])
    def confirmed(self, request):
        """Get confirmed orders"""
        orders = self.get_queryset().filter(status="confirmed")
        serializer = OrderListSerializer(orders, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Cancel order",
        description="Cancel a pending order",
        tags=["Orders"],
        request=OrderCancelSerializer,
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel an order"""
        order = self.get_object()
        serializer = OrderCancelSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Order cancelled successfully",
                "order": OrderDetailSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Confirm payment (DEPRECATED - Testing Only)",
        description="""
        ⚠️ DEPRECATED: This endpoint is for testing purposes only.
        
        In production, payments are automatically confirmed via Stripe webhooks 
        when the payment_intent.succeeded event is received. 
        
        DO NOT use this endpoint in production as it bypasses webhook security 
        and can lead to inventory inconsistencies.
        """,
        tags=["Orders"],
        request=OrderConfirmPaymentSerializer,
    )
    @action(detail=True, methods=["post"])
    def confirm_payment(self, request, pk=None):
        """
        Confirm payment for an order

        ⚠️ WARNING: This is a deprecated testing endpoint.
        In production, use Stripe webhooks for payment confirmation.
        """
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"DEPRECATED: Manual payment confirmation called for order {pk}. "
            "This should only be used for testing. Use webhooks in production."
        )

        order = self.get_object()
        serializer = OrderConfirmPaymentSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Payment confirmed successfully",
                "warning": "This endpoint is deprecated. Use Stripe webhooks in production.",
                "order": OrderDetailSerializer(order).data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Get order statistics",
        description="Get statistics about user's orders",
        tags=["Orders"],
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get order statistics for user"""
        user = request.user
        orders = Order.objects.filter(user=user)

        stats = {
            "total_orders": orders.count(),
            "pending_orders": orders.filter(status="pending").count(),
            "confirmed_orders": orders.filter(status="confirmed").count(),
            "cancelled_orders": orders.filter(status="cancelled").count(),
            "total_spent": orders.filter(status="confirmed").aggregate(
                total=Sum("total_amount")
            )["total"]
            or 0,
            "total_tickets": OrderItem.objects.filter(
                order__user=user, order__status="confirmed"
            ).aggregate(total=Sum("quantity"))["total"]
            or 0,
        }

        return Response(stats)

    @extend_schema(
        summary="Get user's tickets",
        description="Get all tickets purchased by the user across all orders",
        tags=["Orders"],
    )
    @action(detail=False, methods=["get"])
    def my_tickets(self, request):
        """Get all tickets for user across all confirmed orders"""
        user = request.user
        tickets = OrderItem.objects.filter(
            order__user=user, order__status="confirmed"
        ).select_related(
            "order", "ticket_type", "ticket_tier", "day_pass", "day_tier_price"
        )

        serializer = OrderItemSerializer(tickets, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Check for expired orders",
        description="Check and update expired pending orders (Admin only)",
        tags=["Orders"],
    )
    @action(detail=False, methods=["post"])
    def cleanup_expired(self, request):
        """Mark expired pending orders as failed (Admin only)"""
        # Explicit authentication check
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Explicit admin check - only admins should trigger system cleanup
        if not request.user.is_staff:
            return Response(
                {"detail": "Only administrators can trigger order cleanup."},
                status=status.HTTP_403_FORBIDDEN,
            )

        now = timezone.now()
        expired_orders = Order.objects.filter(status="pending", expires_at__lt=now)

        count = expired_orders.count()
        expired_orders.update(
            status="failed",
            cancellation_reason="Order expired - payment not completed in time",
        )

        return Response(
            {"message": f"{count} expired orders marked as failed", "count": count},
            status=status.HTTP_200_OK,
        )

    # ==================== Payment Actions ====================

    @extend_schema(
        summary="Create Stripe Payment Intent",
        description="Create a payment intent for order checkout",
        tags=["Orders", "Payments"],
        responses={200: dict, 400: dict},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="create-payment-intent",
        throttle_classes=[PaymentThrottle],  # Rate limit: 10 requests per hour
    )
    def create_payment_intent(self, request, pk=None):
        """
        Create Stripe Payment Intent for an order

        This generates a client_secret that the frontend uses with Stripe.js
        to collect payment information securely.
        """
        order = self.get_object()

        # Validate order status
        if order.status not in ["pending", "processing"]:
            return Response(
                {"error": "Order cannot be paid", "status": order.status},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate order has items
        if not order.items.exists():
            return Response(
                {"error": "Order has no items"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Calculate service fee (5% of subtotal)
            fee_percentage = Decimal(
                str(getattr(settings, "STRIPE_SERVICE_FEE_PERCENTAGE", 5.0))
            )
            service_fee = (order.subtotal * fee_percentage / Decimal("100")).quantize(
                Decimal("0.01")
            )
            total_amount = order.subtotal + service_fee - order.discount_amount

            # Update order with fees
            order.service_fee = service_fee
            order.total_amount = max(Decimal("0.00"), total_amount)
            order.save(update_fields=["service_fee", "total_amount"])

            # Convert to cents for Stripe
            amount_cents = int(order.total_amount * Decimal("100"))

            # Create Stripe PaymentIntent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=order.currency.lower(),
                metadata={
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "event_id": str(order.event.id),
                    "user_id": str(order.user.id),
                    "expires_at": (
                        order.expires_at.isoformat() if order.expires_at else None
                    ),
                },
                description=f"Order {order.order_number} - {order.event.title}",
                receipt_email=order.buyer_email or order.user.email,
                automatic_payment_methods={"enabled": True},
            )

            # Update order with payment info
            order.payment_id = payment_intent.id
            order.payment_method = "stripe"
            order.status = "processing"
            order.save(update_fields=["payment_id", "payment_method", "status"])

            logger.info(f"Payment intent created for order {order.order_number}")

            return Response(
                {
                    "success": True,
                    "payment_intent": {
                        "client_secret": payment_intent.client_secret,
                        "payment_intent_id": payment_intent.id,
                        "amount": amount_cents,
                        "currency": order.currency.lower(),
                        "status": payment_intent.status,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error for order {order.id}: {str(e)}")
            return Response(
                {"error": f"Payment processing error: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(
                f"Error creating payment intent for order {order.id}: {str(e)}"
            )
            return Response(
                {"error": "Failed to create payment intent"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Get Payment Status",
        description="Check the current status of a payment",
        tags=["Orders", "Payments"],
    )
    @action(detail=True, methods=["get"], url_path="payment-status")
    def payment_status(self, request, pk=None):
        """Get current payment status for an order"""
        order = self.get_object()

        if not order.payment_id:
            return Response(
                {"error": "No payment found for this order"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Retrieve payment intent from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(order.payment_id)

            return Response(
                {
                    "order_id": str(order.id),
                    "order_number": order.order_number,
                    "order_status": order.status,
                    "payment_status": payment_intent.status,
                    "amount": payment_intent.amount / 100,
                    "currency": payment_intent.currency,
                },
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            logger.error(
                f"Stripe error retrieving payment for order {order.id}: {str(e)}"
            )
            return Response(
                {"error": f"Failed to retrieve payment status: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Refund Order",
        description="Process a full or partial refund for an order",
        tags=["Orders", "Payments"],
    )
    @action(detail=True, methods=["post"], url_path="refund")
    def refund_order(self, request, pk=None):
        """
        Process a refund for a confirmed order

        Body params:
        - amount (optional): Partial refund amount. If not provided, full refund.
        - reason (optional): Reason for refund
        """
        order = self.get_object()

        # Validate order can be refunded
        if order.status in ["refunded", "cancelled", "failed"]:
            return Response(
                {
                    "error": f"Cannot refund order with status: {order.status}",
                    "current_status": order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not order.payment_id:
            return Response(
                {"error": "No payment found for this order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status != "confirmed":
            return Response(
                {
                    "error": "Only confirmed orders can be refunded",
                    "current_status": order.status,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get refund parameters
            amount = request.data.get("amount")
            reason = request.data.get("reason", "requested_by_customer")

            refund_params = {"payment_intent": order.payment_id}

            # Add amount for partial refund
            if amount:
                refund_params["amount"] = int(Decimal(str(amount)) * Decimal("100"))

            # Add reason if provided
            if reason:
                refund_params["reason"] = reason

            # Create refund in Stripe
            refund = stripe.Refund.create(**refund_params)

            # Update order status
            order.status = "refunded"
            if reason:
                order.cancellation_reason = f"Refund: {reason}"
            order.save(update_fields=["status", "cancellation_reason"])

            logger.info(f"Refund processed for order {order.order_number}")

            # Send refund notification email
            try:
                from Common.email_utils import send_order_cancelled_email

                send_order_cancelled_email(order)
            except Exception as e:
                logger.error(f"Failed to send refund email: {e}")

            return Response(
                {
                    "success": True,
                    "refund_id": refund.id,
                    "amount": refund.amount / 100,
                    "currency": refund.currency,
                    "status": refund.status,
                },
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe refund error for order {order.id}: {str(e)}")
            return Response(
                {"error": f"Refund failed: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
