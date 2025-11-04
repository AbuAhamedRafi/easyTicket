"""
Payment API Views
Handles payment-related API endpoints
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from decimal import Decimal

from .models import Order
from .payment_service import StripePaymentService
from .permissions import IsOrderOwner


class PaymentIntentView(APIView):
    """Create a Stripe Payment Intent for an order"""

    permission_classes = [IsAuthenticated, IsOrderOwner]

    @extend_schema(
        summary="Create Payment Intent",
        description="Create a Stripe PaymentIntent for checkout",
        responses={200: dict, 400: dict, 404: dict},
    )
    def post(self, request, order_id):
        """Create payment intent for order"""
        # Get order
        order = get_object_or_404(Order, id=order_id, user=request.user)

        # Validate order status
        if order.status not in ["pending", "processing"]:
            return Response(
                {"error": "Order cannot be paid", "status": order.status},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate order has items
        if not order.items.exists():
            return Response(
                {"error": "Order has no items"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create payment intent
            payment_data = StripePaymentService.create_payment_intent(order)

            return Response(
                {
                    "success": True,
                    "payment_intent": payment_data,
                    "order": {
                        "id": str(order.id),
                        "order_number": order.order_number,
                        "subtotal": str(order.subtotal),
                        "service_fee": str(order.service_fee),
                        "total_amount": str(order.total_amount),
                        "currency": order.currency,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConfirmPaymentView(APIView):
    """Confirm a payment after Stripe processing"""

    permission_classes = [IsAuthenticated, IsOrderOwner]

    @extend_schema(
        summary="Confirm Payment",
        description="Confirm payment and update order status",
        request={
            "application/json": {
                "type": "object",
                "properties": {"payment_intent_id": {"type": "string"}},
                "required": ["payment_intent_id"],
            }
        },
        responses={200: dict, 400: dict},
    )
    def post(self, request, order_id):
        """Confirm payment for order"""
        order = get_object_or_404(Order, id=order_id, user=request.user)

        payment_intent_id = request.data.get("payment_intent_id")
        if not payment_intent_id:
            return Response(
                {"error": "payment_intent_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Confirm payment
            success = StripePaymentService.confirm_payment(order, payment_intent_id)

            if success:
                # Refresh order data
                order.refresh_from_db()

                return Response(
                    {
                        "success": True,
                        "message": "Payment confirmed successfully",
                        "order": {
                            "id": str(order.id),
                            "order_number": order.order_number,
                            "status": order.status,
                            "total_amount": str(order.total_amount),
                            "paid_at": (
                                order.paid_at.isoformat() if order.paid_at else None
                            ),
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Payment confirmation failed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefundView(APIView):
    """Request a refund for an order"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Request Refund",
        description="Create a refund for a confirmed order",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Partial refund amount (optional)",
                    },
                    "reason": {"type": "string", "description": "Refund reason"},
                },
            }
        },
        responses={200: dict, 400: dict},
    )
    def post(self, request, order_id):
        """Request refund for order"""
        order = get_object_or_404(Order, id=order_id)

        # Check permissions (user must own order or be organizer)
        if order.user != request.user and order.event.organizer != request.user:
            return Response(
                {"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN
            )

        # Get refund parameters
        amount = request.data.get("amount")
        if amount:
            amount = Decimal(str(amount))

        reason = request.data.get("reason", "requested_by_customer")

        try:
            # Create refund
            refund_data = StripePaymentService.create_refund(order, amount, reason)

            return Response(
                {
                    "success": True,
                    "message": "Refund processed successfully",
                    "refund": refund_data,
                    "order": {
                        "id": str(order.id),
                        "order_number": order.order_number,
                        "status": order.status,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentStatusView(APIView):
    """Check payment status for an order"""

    permission_classes = [IsAuthenticated, IsOrderOwner]

    @extend_schema(
        summary="Get Payment Status",
        description="Retrieve current payment status from Stripe",
        responses={200: dict, 404: dict},
    )
    def get(self, request, order_id):
        """Get payment status"""
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if not order.payment_id:
            return Response(
                {
                    "status": order.status,
                    "payment_status": None,
                    "message": "No payment initiated",
                },
                status=status.HTTP_200_OK,
            )

        try:
            # Get payment intent from Stripe
            payment_data = StripePaymentService.retrieve_payment_intent(
                order.payment_id
            )

            return Response(
                {
                    "order_status": order.status,
                    "payment": payment_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
