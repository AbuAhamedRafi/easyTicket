"""
Serializers for Events app
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Event, EventCategory


class EventCategorySerializer(serializers.ModelSerializer):
    """Serializer for Event Categories"""

    events_count = serializers.SerializerMethodField()

    class Meta:
        model = EventCategory
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "icon",
            "is_active",
            "events_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_events_count(self, obj):
        """Get count of published events in this category"""
        return obj.events.filter(status="published").count()


class EventListSerializer(serializers.ModelSerializer):
    """Serializer for Event list view (minimal fields)"""

    organizer_name = serializers.CharField(
        source="organizer.get_full_name", read_only=True
    )
    organizer_email = serializers.EmailField(source="organizer.email", read_only=True)
    category_name = serializers.CharField(
        source="category.name", read_only=True, allow_null=True
    )
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "slug",
            "short_description",
            "organizer",
            "organizer_name",
            "organizer_email",
            "category",
            "category_name",
            "venue_name",
            "venue_city",
            "venue_country",
            "start_date",
            "end_date",
            "thumbnail_image",
            "status",
            "is_free",
            "base_price",
            "currency",
            "is_featured",
            "is_upcoming",
            "is_ongoing",
            "is_past",
            "duration_days",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "organizer",
            "created_at",
            "is_upcoming",
            "is_ongoing",
            "is_past",
        ]


class EventDetailSerializer(serializers.ModelSerializer):
    """Serializer for Event detail view (all fields)"""

    organizer_name = serializers.CharField(
        source="organizer.get_full_name", read_only=True
    )
    organizer_email = serializers.EmailField(source="organizer.email", read_only=True)
    category_details = EventCategorySerializer(source="category", read_only=True)
    is_upcoming = serializers.ReadOnlyField()
    is_ongoing = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    duration_days = serializers.ReadOnlyField()
    available_tickets = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = [
            "id",
            "slug",
            "organizer",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def get_available_tickets(self, obj):
        """Get available tickets count"""
        return obj.get_available_tickets_count()


class EventCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating events"""

    # Make category optional and accept null
    category = serializers.PrimaryKeyRelatedField(
        queryset=EventCategory.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "short_description",
            "category",
            "venue_name",
            "venue_address",
            "venue_city",
            "venue_state",
            "venue_country",
            "venue_postal_code",
            "venue_latitude",
            "venue_longitude",
            "start_date",
            "end_date",
            "banner_image",
            "thumbnail_image",
            "total_capacity",
            "status",
            "is_free",
            "base_price",
            "currency",
            "terms_and_conditions",
            "refund_policy",
            "age_restriction",
            "tags",
            "is_featured",
        ]

    def validate(self, attrs):
        """Validate event data"""
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        is_free = attrs.get("is_free", False)
        base_price = attrs.get("base_price", 0)

        # Validate dates
        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError(
                    {"end_date": "End date must be after start date"}
                )

            if start_date < timezone.now():
                raise serializers.ValidationError(
                    {"start_date": "Start date cannot be in the past"}
                )

        # Validate pricing
        if not is_free and base_price <= 0:
            raise serializers.ValidationError(
                {"base_price": "Base price must be greater than 0 for paid events"}
            )

        if is_free and base_price > 0:
            raise serializers.ValidationError(
                {"is_free": "Free events cannot have a base price"}
            )

        return attrs

    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance:  # Update
            old_status = self.instance.status

            # Don't allow changing from completed/cancelled to other statuses
            if old_status in ["completed", "cancelled"] and value != old_status:
                raise serializers.ValidationError(
                    f"Cannot change status from {old_status} to {value}"
                )

        return value

    def create(self, validated_data):
        """Create event with organizer"""
        # Organizer will be set in the view
        return super().create(validated_data)

    def to_representation(self, instance):
        """Return detailed representation after create/update"""
        return EventDetailSerializer(instance, context=self.context).data
