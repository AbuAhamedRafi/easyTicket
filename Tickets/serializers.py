"""
Serializers for Tickets app
"""

from django.db import transaction
from rest_framework import serializers
from django.utils import timezone
from .models import TicketType, TicketTier, DayPass, DayTierPrice, Ticket


class TicketTierSerializer(serializers.ModelSerializer):
    """Serializer for Ticket Tiers"""

    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()

    class Meta:
        model = TicketTier
        fields = [
            "uid",
            "tier_number",
            "name",
            "price",
            "quantity",
            "quantity_sold",
            "available_quantity",
            "is_sold_out",
            "sales_start",
            "sales_end",
            "created_at",
        ]
        read_only_fields = ["uid", "quantity_sold", "created_at"]

    def validate(self, attrs):
        """Validate tier data"""
        sales_start = attrs.get("sales_start")
        sales_end = attrs.get("sales_end")

        if sales_start and sales_end and sales_end <= sales_start:
            raise serializers.ValidationError(
                {"sales_end": "Sales end date must be after sales start date"}
            )

        return attrs


class DayPassSerializer(serializers.ModelSerializer):
    """Serializer for Day Passes"""

    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()

    class Meta:
        model = DayPass
        fields = [
            "uid",
            "day_number",
            "name",
            "date",
            "price",
            "quantity",
            "quantity_sold",
            "available_quantity",
            "is_sold_out",
            "is_all_days",
            "created_at",
        ]
        read_only_fields = ["uid", "quantity_sold", "created_at"]

    def validate(self, attrs):
        """Validate day pass data"""
        is_all_days = attrs.get("is_all_days", False)
        day_number = attrs.get("day_number")

        if is_all_days and day_number is not None:
            raise serializers.ValidationError(
                {"day_number": "All days pass should not have a day number"}
            )

        if not is_all_days and day_number is None:
            raise serializers.ValidationError(
                {"day_number": "Single day pass must have a day number"}
            )

        return attrs


class DayTierPriceSerializer(serializers.ModelSerializer):
    """Serializer for Day + Tier pricing combinations"""

    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()

    class Meta:
        model = DayTierPrice
        fields = [
            "uid",
            "day_number",
            "day_name",
            "date",
            "tier_number",
            "tier_name",
            "price",
            "quantity",
            "quantity_sold",
            "available_quantity",
            "is_sold_out",
            "is_on_sale",
            "is_active",
            "sales_start",
            "sales_end",
            "created_at",
        ]
        read_only_fields = ["uid", "quantity_sold", "created_at"]

    def validate(self, attrs):
        """Validate day tier price data"""
        sales_start = attrs.get("sales_start")
        sales_end = attrs.get("sales_end")

        if sales_start and sales_end and sales_end <= sales_start:
            raise serializers.ValidationError(
                {"sales_end": "Sales end date must be after sales start date"}
            )

        # Validate day and tier numbers are positive
        day_number = attrs.get("day_number")
        tier_number = attrs.get("tier_number")

        if day_number and day_number < 1:
            raise serializers.ValidationError(
                {"day_number": "Day number must be positive"}
            )

        if tier_number and tier_number < 1:
            raise serializers.ValidationError(
                {"tier_number": "Tier number must be positive"}
            )

        return attrs


class TicketTypeListSerializer(serializers.ModelSerializer):
    """Serializer for listing ticket types (minimal info)"""

    event_title = serializers.CharField(source="event.title", read_only=True)
    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    min_price = serializers.ReadOnlyField()

    class Meta:
        model = TicketType
        fields = [
            "uid",
            "event",
            "event_title",
            "name",
            "description",
            "pricing_type",
            "price",
            "min_price",
            "total_quantity",
            "quantity_sold",
            "available_quantity",
            "is_sold_out",
            "is_on_sale",
            "sales_start",
            "sales_end",
            "is_active",
            "created_at",
        ]


class TicketTypeDetailSerializer(serializers.ModelSerializer):
    """Serializer for ticket type details with nested tiers/days"""

    event_title = serializers.CharField(source="event.title", read_only=True)
    event_slug = serializers.CharField(source="event.slug", read_only=True)
    tiers = TicketTierSerializer(many=True, read_only=True)
    day_passes = DayPassSerializer(many=True, read_only=True)
    day_tier_prices = DayTierPriceSerializer(many=True, read_only=True)
    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    min_price = serializers.ReadOnlyField()

    class Meta:
        model = TicketType
        fields = "__all__"
        read_only_fields = ["uid", "quantity_sold", "created_at", "updated_at"]


class TicketTypeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ticket types"""

    tiers = TicketTierSerializer(many=True, required=False)
    day_passes = DayPassSerializer(many=True, required=False)
    day_tier_prices = DayTierPriceSerializer(many=True, required=False)

    class Meta:
        model = TicketType
        fields = [
            "event",
            "name",
            "description",
            "pricing_type",
            "price",
            "total_quantity",
            "sales_start",
            "sales_end",
            "min_purchase",
            "max_purchase",
            "benefits",
            "is_active",
            "tiers",
            "day_passes",
            "day_tier_prices",
        ]

    def validate(self, attrs):
        """Validate ticket type data"""
        pricing_type = attrs.get("pricing_type")
        price = attrs.get("price")
        tiers = attrs.get("tiers", [])
        day_passes = attrs.get("day_passes", [])
        sales_start = attrs.get("sales_start")
        sales_end = attrs.get("sales_end")
        min_purchase = attrs.get("min_purchase", 1)
        max_purchase = attrs.get("max_purchase", 10)

        # Validate pricing type requirements
        if pricing_type == "simple":
            if not price:
                raise serializers.ValidationError(
                    {"price": "Price is required for simple pricing type"}
                )
        else:
            # For non-simple pricing types, price should be null
            attrs["price"] = None

        # Note: Tiers and day passes can be created separately after ticket type creation
        # So we don't enforce them during creation, only during validation if provided

        # Validate sales period
        if sales_start and sales_end and sales_end <= sales_start:
            raise serializers.ValidationError(
                {"sales_end": "Sales end date must be after sales start date"}
            )

        # Validate purchase limits
        if min_purchase > max_purchase:
            raise serializers.ValidationError(
                {
                    "min_purchase": "Minimum purchase cannot be greater than maximum purchase"
                }
            )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create ticket type with nested tiers/days/day_tier_prices"""
        tiers_data = validated_data.pop("tiers", [])
        day_passes_data = validated_data.pop("day_passes", [])
        day_tier_prices_data = validated_data.pop("day_tier_prices", [])

        ticket_type = TicketType.objects.create(**validated_data)

        # Create tiers (for 'tiered' pricing)
        for tier_data in tiers_data:
            TicketTier.objects.create(ticket_type=ticket_type, **tier_data)

        # Create day passes (for 'day_based' pricing)
        for day_pass_data in day_passes_data:
            DayPass.objects.create(ticket_type=ticket_type, **day_pass_data)

        # Create day tier prices (for 'tier_and_day' pricing)
        for day_tier_data in day_tier_prices_data:
            DayTierPrice.objects.create(ticket_type=ticket_type, **day_tier_data)

        return ticket_type

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update ticket type (tiers/days/day_tier_prices updated separately)"""
        tiers_data = validated_data.pop("tiers", None)
        day_passes_data = validated_data.pop("day_passes", None)
        day_tier_prices_data = validated_data.pop("day_tier_prices", None)

        # Update ticket type fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Note: For simplicity, tiers, day passes, and day_tier_prices should be updated via separate endpoints
        # This prevents accidental deletion of existing pricing options

        return instance

    def to_representation(self, instance):
        """Return detailed representation after create/update"""
        return TicketTypeDetailSerializer(instance, context=self.context).data


# ==================== Individual Ticket Serializers ====================


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for individual tickets"""

    event_title = serializers.CharField(source="event.title", read_only=True)
    event_date_formatted = serializers.SerializerMethodField()
    venue = serializers.SerializerMethodField()
    full_ticket_name = serializers.ReadOnlyField()
    is_valid = serializers.ReadOnlyField()
    order_number = serializers.CharField(
        source="order_item.order.order_number", read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "uid",
            "ticket_number",
            "qr_code_data",
            "event",
            "event_title",
            "event_date",
            "event_date_formatted",
            "venue",
            "ticket_name",
            "tier_name",
            "day_name",
            "full_ticket_name",
            "price",
            "status",
            "is_used",
            "used_at",
            "is_valid",
            "attendee_name",
            "attendee_email",
            "order_number",
            "created_at",
        ]
        read_only_fields = [
            "uid",
            "ticket_number",
            "qr_code_data",
            "event",
            "ticket_name",
            "tier_name",
            "day_name",
            "event_date",
            "price",
            "is_used",
            "used_at",
            "created_at",
        ]

    def get_event_date_formatted(self, obj):
        """Format event date for display"""
        return obj.event_date.strftime("%A, %B %d, %Y at %I:%M %p")

    def get_venue(self, obj):
        """Get venue information"""
        return {
            "name": obj.event.venue_name,
            "address": obj.event.venue_address,
            "city": obj.event.venue_city,
        }


class TicketVerificationSerializer(serializers.Serializer):
    """Serializer for ticket verification via QR code"""

    qr_code_data = serializers.CharField(required=True)

    def validate_qr_code_data(self, value):
        """Validate QR code exists"""
        try:
            ticket = Ticket.objects.get(qr_code_data=value)
            self.context["ticket"] = ticket
            return value
        except Ticket.DoesNotExist:
            raise serializers.ValidationError("Invalid QR code. Ticket not found.")

    def validate(self, attrs):
        """Validate ticket can be used"""
        ticket = self.context.get("ticket")

        if not ticket:
            raise serializers.ValidationError("Ticket not found.")

        # Check if already used
        if ticket.is_used:
            raise serializers.ValidationError(
                {
                    "error": "Ticket already used",
                    "used_at": ticket.used_at,
                    "scanned_by": (
                        ticket.scanned_by.email if ticket.scanned_by else None
                    ),
                }
            )

        # Check status
        if ticket.status != "active":
            raise serializers.ValidationError(
                {
                    "error": f"Ticket is {ticket.status}",
                    "status": ticket.status,
                }
            )

        # Check if event has ended
        if ticket.event.end_date and timezone.now() > ticket.event.end_date:
            raise serializers.ValidationError(
                {
                    "error": "Event has ended",
                    "event_end_date": ticket.event.end_date,
                }
            )

        return attrs

    def save(self):
        """Mark ticket as used"""
        ticket = self.context.get("ticket")
        scanner = self.context.get("scanner")  # User who scanned the ticket

        ticket.mark_as_used(scanned_by_user=scanner)

        return ticket
