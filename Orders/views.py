"""
Views for Orders app
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

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
        summary="Confirm payment",
        description="Confirm payment for an order (admin/payment gateway use)",
        tags=["Orders"],
        request=OrderConfirmPaymentSerializer,
    )
    @action(detail=True, methods=["post"])
    def confirm_payment(self, request, pk=None):
        """Confirm payment for an order"""
        order = self.get_object()
        serializer = OrderConfirmPaymentSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Payment confirmed successfully",
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
        ).select_related("order", "ticket_type", "ticket_tier", "day_pass")

        serializer = OrderItemSerializer(tickets, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Check for expired orders",
        description="Check and update expired pending orders",
        tags=["Orders"],
    )
    @action(detail=False, methods=["post"])
    def cleanup_expired(self, request):
        """Mark expired pending orders as failed"""
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
