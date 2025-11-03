"""
Serializers for Tickets app
"""

from rest_framework import serializers
from django.utils import timezone
from .models import TicketType, TicketTier, DayPass


class TicketTierSerializer(serializers.ModelSerializer):
    """Serializer for Ticket Tiers"""

    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()

    class Meta:
        model = TicketTier
        fields = [
            "id",
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
        read_only_fields = ["id", "quantity_sold", "created_at"]

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
            "id",
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
        read_only_fields = ["id", "quantity_sold", "created_at"]

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
            "id",
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
    available_quantity = serializers.ReadOnlyField()
    is_sold_out = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    min_price = serializers.ReadOnlyField()

    class Meta:
        model = TicketType
        fields = "__all__"
        read_only_fields = ["id", "quantity_sold", "created_at", "updated_at"]


class TicketTypeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating ticket types"""

    tiers = TicketTierSerializer(many=True, required=False)
    day_passes = DayPassSerializer(many=True, required=False)

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
        if pricing_type == "simple" and not price:
            raise serializers.ValidationError(
                {"price": "Price is required for simple pricing type"}
            )

        if pricing_type == "tiered" and not tiers:
            raise serializers.ValidationError(
                {"tiers": "At least one tier is required for tiered pricing"}
            )

        if pricing_type == "day_based" and not day_passes:
            raise serializers.ValidationError(
                {
                    "day_passes": "At least one day pass is required for day-based pricing"
                }
            )

        if pricing_type == "tier_and_day" and (not tiers or not day_passes):
            raise serializers.ValidationError(
                "Both tiers and day passes are required for tier + day pricing"
            )

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

    def create(self, validated_data):
        """Create ticket type with nested tiers/days"""
        tiers_data = validated_data.pop("tiers", [])
        day_passes_data = validated_data.pop("day_passes", [])

        ticket_type = TicketType.objects.create(**validated_data)

        # Create tiers
        for tier_data in tiers_data:
            TicketTier.objects.create(ticket_type=ticket_type, **tier_data)

        # Create day passes
        for day_pass_data in day_passes_data:
            DayPass.objects.create(ticket_type=ticket_type, **day_pass_data)

        return ticket_type

    def update(self, instance, validated_data):
        """Update ticket type (tiers/days updated separately)"""
        tiers_data = validated_data.pop("tiers", None)
        day_passes_data = validated_data.pop("day_passes", None)

        # Update ticket type fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Note: For simplicity, tiers and day passes should be updated via separate endpoints
        # This prevents accidental deletion of existing tiers/days

        return instance

    def to_representation(self, instance):
        """Return detailed representation after create/update"""
        return TicketTypeDetailSerializer(instance, context=self.context).data
