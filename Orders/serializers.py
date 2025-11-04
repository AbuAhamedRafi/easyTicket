"""
Serializers for Orders app
Handles order creation, validation, and payment processing
"""

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

from .models import Order, OrderItem
from Tickets.models import TicketType, TicketTier, DayPass
from Events.models import Event


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem (read-only, for displaying order items)"""

    full_ticket_name = serializers.CharField(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "ticket_type",
            "ticket_tier",
            "day_pass",
            "quantity",
            "unit_price",
            "subtotal",
            "ticket_name",
            "tier_name",
            "day_name",
            "full_ticket_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "subtotal",
            "ticket_name",
            "tier_name",
            "day_name",
            "full_ticket_name",
            "created_at",
        ]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items (nested in order creation)"""

    ticket_type_id = serializers.UUIDField()
    ticket_tier_id = serializers.UUIDField(required=False, allow_null=True)
    day_pass_id = serializers.UUIDField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        """
        Validate ticket availability and pricing
        
        This method:
        1. Locks the ticket row to prevent race conditions
        2. Checks if ticket is on sale
        3. Validates quantity availability  
        4. Determines pricing based on ticket type (simple/tiered/day-based/combined)
        5. Returns validated data with price information
        """
        ticket_type_id = data.get("ticket_type_id")
        ticket_tier_id = data.get("ticket_tier_id")
        day_pass_id = data.get("day_pass_id")
        quantity = data.get("quantity")

        # Get ticket type with row lock to prevent race conditions
        try:
            ticket_type = (
                TicketType.objects.select_for_update()
                .select_related("event")
                .get(id=ticket_type_id)
            )
        except TicketType.DoesNotExist:
            raise serializers.ValidationError("Ticket type not found")

        # Check if ticket is on sale
        if not ticket_type.is_on_sale:
            raise serializers.ValidationError(
                f"Ticket '{ticket_type.name}' is not currently on sale"
            )

        # Check quantity availability with locked row
        available = ticket_type.available_quantity
        if available is not None and quantity > available:
            raise serializers.ValidationError(
                f"Only {available} tickets available for '{ticket_type.name}'"
            )

        # Validate pricing type and get price
        pricing_type = ticket_type.pricing_type

        if pricing_type == "simple":
            # Simple pricing - no tier or day pass
            if ticket_tier_id or day_pass_id:
                raise serializers.ValidationError(
                    "This ticket type does not use tiers or day passes"
                )
            unit_price = ticket_type.price

        elif pricing_type == "tiered":
            # Tiered pricing - requires tier
            if not ticket_tier_id:
                raise serializers.ValidationError(
                    "Ticket tier is required for this ticket type"
                )
            if day_pass_id:
                raise serializers.ValidationError(
                    "This ticket type does not use day passes"
                )

            try:
                tier = TicketTier.objects.get(
                    id=ticket_tier_id, ticket_type=ticket_type
                )
            except TicketTier.DoesNotExist:
                raise serializers.ValidationError("Invalid ticket tier")

            # Check tier quantity
            tier_available = tier.available_quantity
            if tier_available is not None and quantity > tier_available:
                raise serializers.ValidationError(
                    f"Only {tier_available} tickets available for tier '{tier.name}'"
                )

            unit_price = tier.price
            data["tier"] = tier

        elif pricing_type == "day_based":
            # Day-based pricing - requires day pass
            if not day_pass_id:
                raise serializers.ValidationError(
                    "Day pass is required for this ticket type"
                )
            if ticket_tier_id:
                raise serializers.ValidationError("This ticket type does not use tiers")

            try:
                day_pass = DayPass.objects.get(id=day_pass_id, ticket_type=ticket_type)
            except DayPass.DoesNotExist:
                raise serializers.ValidationError("Invalid day pass")

            # Check day pass quantity
            day_available = day_pass.available_quantity
            if day_available is not None and quantity > day_available:
                raise serializers.ValidationError(
                    f"Only {day_available} tickets available for '{day_pass.name}'"
                )

            unit_price = day_pass.price
            data["day_pass"] = day_pass

        elif pricing_type == "tier_and_day":
            # Combination pricing - requires both tier and day pass
            if not ticket_tier_id or not day_pass_id:
                raise serializers.ValidationError(
                    "Both ticket tier and day pass are required for this ticket type"
                )

            try:
                tier = TicketTier.objects.get(
                    id=ticket_tier_id, ticket_type=ticket_type
                )
            except TicketTier.DoesNotExist:
                raise serializers.ValidationError("Invalid ticket tier")

            try:
                day_pass = DayPass.objects.get(id=day_pass_id, ticket_type=ticket_type)
            except DayPass.DoesNotExist:
                raise serializers.ValidationError("Invalid day pass")

            # Check quantities (use minimum of both)
            tier_available = tier.available_quantity
            day_available = day_pass.available_quantity

            if tier_available is not None and quantity > tier_available:
                raise serializers.ValidationError(
                    f"Only {tier_available} tickets available for tier '{tier.name}'"
                )
            if day_available is not None and quantity > day_available:
                raise serializers.ValidationError(
                    f"Only {day_available} tickets available for day '{day_pass.name}'"
                )

            # Price is sum of tier and day pass
            unit_price = tier.price + day_pass.price
            data["tier"] = tier
            data["day_pass"] = day_pass

        else:
            raise serializers.ValidationError("Invalid pricing type")

        # Store ticket type and price in validated data
        data["ticket_type"] = ticket_type
        data["unit_price"] = unit_price

        return data


class OrderListSerializer(serializers.ModelSerializer):
    """Minimal serializer for listing orders"""

    event_name = serializers.CharField(source="event.title", read_only=True)
    total_tickets = serializers.IntegerField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "event",
            "event_name",
            "status",
            "total_amount",
            "currency",
            "total_tickets",
            "is_paid",
            "is_expired",
            "created_at",
            "expires_at",
        ]
        read_only_fields = ["id", "order_number", "created_at"]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for order details"""

    items = OrderItemSerializer(many=True, read_only=True)
    event_name = serializers.CharField(source="event.title", read_only=True)
    event_image = serializers.ImageField(source="event.banner", read_only=True)
    event_date = serializers.DateTimeField(source="event.start_date", read_only=True)
    event_location = serializers.CharField(source="event.city", read_only=True)
    total_tickets = serializers.IntegerField(read_only=True)
    is_paid = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "user",
            "event",
            "event_name",
            "event_image",
            "event_date",
            "event_location",
            "status",
            "subtotal",
            "service_fee",
            "discount_amount",
            "total_amount",
            "currency",
            "payment_method",
            "payment_id",
            "paid_at",
            "buyer_email",
            "buyer_phone",
            "buyer_name",
            "promo_code",
            "notes",
            "cancellation_reason",
            "cancelled_at",
            "items",
            "total_tickets",
            "is_paid",
            "is_expired",
            "created_at",
            "updated_at",
            "expires_at",
        ]
        read_only_fields = [
            "id",
            "order_number",
            "user",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""

    items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "event",
            "items",
            "buyer_email",
            "buyer_phone",
            "buyer_name",
            "notes",
            "promo_code",
        ]

    def validate_items(self, items):
        """Ensure at least one item"""
        if not items:
            raise serializers.ValidationError("Order must have at least one item")
        return items

    def validate_event(self, event):
        """Ensure event exists and is published"""
        if event.status != "published":
            raise serializers.ValidationError(
                "Cannot create order for unpublished event"
            )
        return event

    @transaction.atomic
    def create(self, validated_data):
        """Create order with items"""
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        # Calculate subtotal first before creating order
        subtotal = Decimal("0.00")
        for item_data in items_data:
            unit_price = item_data["unit_price"]
            quantity = item_data["quantity"]
            subtotal += unit_price * quantity

        # Create order with initial subtotal
        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            total_amount=subtotal,  # Will be recalculated with fees
            **validated_data,
        )

        # Create order items
        for item_data in items_data:
            ticket_type = item_data["ticket_type"]
            unit_price = item_data["unit_price"]
            quantity = item_data["quantity"]

            # Create order item
            OrderItem.objects.create(
                order=order,
                ticket_type=ticket_type,
                ticket_tier=item_data.get("tier"),
                day_pass=item_data.get("day_pass"),
                quantity=quantity,
                unit_price=unit_price,
            )

        # Recalculate totals with fees
        order.calculate_totals()

        return order


class OrderCancelSerializer(serializers.Serializer):
    """Serializer for cancelling an order"""

    reason = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, data):
        """Ensure order can be cancelled"""
        order = self.instance

        if order.status in ["cancelled", "refunded"]:
            raise serializers.ValidationError(f"Order is already {order.status}")

        if order.status == "confirmed":
            raise serializers.ValidationError(
                "Cannot cancel confirmed order. Please request a refund instead."
            )

        return data

    def update(self, instance, validated_data):
        """Cancel the order"""
        reason = validated_data.get("reason", "Customer cancellation")
        instance.cancel_order(reason)
        return instance


class OrderConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming payment"""

    payment_id = serializers.CharField(max_length=255)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)

    def validate(self, data):
        """Ensure order can be confirmed"""
        order = self.instance

        if order.status == "confirmed":
            raise serializers.ValidationError("Order is already confirmed")

        if order.status in ["cancelled", "refunded"]:
            raise serializers.ValidationError(f"Cannot confirm {order.status} order")

        if order.is_expired:
            raise serializers.ValidationError("Order has expired")

        return data

    def update(self, instance, validated_data):
        """Confirm the payment"""
        instance.confirm_payment(
            payment_id=validated_data["payment_id"],
            payment_method=validated_data["payment_method"],
        )
        return instance
