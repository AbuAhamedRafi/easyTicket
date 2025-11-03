"""
Views for Events app using ViewSets
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Event, EventCategory
from .serializers import (
    EventListSerializer,
    EventDetailSerializer,
    EventCreateUpdateSerializer,
    EventCategorySerializer,
)
from .permissions import IsOrganizer, IsEventOwner, IsEventOwnerOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="List all event categories",
        description="Get a list of all active event categories",
        tags=["Event Categories"],
    ),
    retrieve=extend_schema(
        summary="Get category details",
        description="Get detailed information about a specific category",
        tags=["Event Categories"],
    ),
    create=extend_schema(
        summary="Create new category",
        description="Create a new event category (Admin only)",
        tags=["Event Categories"],
    ),
    update=extend_schema(
        summary="Update category",
        description="Update an existing category (Admin only)",
        tags=["Event Categories"],
    ),
    partial_update=extend_schema(
        summary="Partially update category",
        description="Partially update a category (Admin only)",
        tags=["Event Categories"],
    ),
    destroy=extend_schema(
        summary="Delete category",
        description="Delete a category (Admin only)",
        tags=["Event Categories"],
    ),
)
class EventCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Event Categories
    - List/Retrieve: Public access
    - Create/Update/Delete: Admin only
    """

    queryset = EventCategory.objects.filter(is_active=True)
    serializer_class = EventCategorySerializer
    lookup_field = "slug"

    def get_permissions(self):
        """Public can view, admin can modify"""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]


@extend_schema_view(
    list=extend_schema(
        summary="List all events",
        description="Get a list of all published events with filtering and search",
        tags=["Events"],
        parameters=[
            OpenApiParameter(
                "status", OpenApiTypes.STR, description="Filter by status"
            ),
            OpenApiParameter(
                "category", OpenApiTypes.UUID, description="Filter by category ID"
            ),
            OpenApiParameter(
                "is_free", OpenApiTypes.BOOL, description="Filter free events"
            ),
            OpenApiParameter(
                "is_featured", OpenApiTypes.BOOL, description="Filter featured events"
            ),
            OpenApiParameter("city", OpenApiTypes.STR, description="Filter by city"),
            OpenApiParameter(
                "search",
                OpenApiTypes.STR,
                description="Search in title, description, tags",
            ),
            OpenApiParameter(
                "ordering",
                OpenApiTypes.STR,
                description="Order by: start_date, -start_date, base_price, -base_price",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get event details",
        description="Get detailed information about a specific event",
        tags=["Events"],
    ),
    create=extend_schema(
        summary="Create new event",
        description="Create a new event (Organizers only)",
        tags=["Events"],
    ),
    update=extend_schema(
        summary="Update event",
        description="Update an existing event (Owner only)",
        tags=["Events"],
    ),
    partial_update=extend_schema(
        summary="Partially update event",
        description="Partially update an event (Owner only)",
        tags=["Events"],
    ),
    destroy=extend_schema(
        summary="Delete event",
        description="Delete an event (Owner only)",
        tags=["Events"],
    ),
)
class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Events
    - List: Public access (only published events for non-owners)
    - Create: Organizers only
    - Retrieve/Update/Delete: Event owner only
    """

    queryset = Event.objects.select_related("organizer", "category").all()
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "category", "is_free", "is_featured", "venue_city"]
    search_fields = [
        "title",
        "description",
        "short_description",
        "tags",
        "venue_name",
        "venue_city",
    ]
    ordering_fields = ["start_date", "created_at", "base_price", "title"]
    ordering = ["-start_date"]

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == "list":
            return EventListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return EventCreateUpdateSerializer
        return EventDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == "list":
            return [AllowAny()]
        elif self.action == "retrieve":
            return [IsAuthenticatedOrReadOnly()]
        elif self.action == "create":
            return [IsAuthenticated(), IsOrganizer()]
        else:  # update, partial_update, destroy
            return [IsAuthenticated(), IsEventOwner()]

    def get_queryset(self):
        """Filter queryset based on user"""
        queryset = super().get_queryset()
        user = self.request.user

        # For list view, show only published events to public
        # Show all events to the organizer who created them
        if self.action == "list":
            if user.is_authenticated:
                if user.user_type == "organizer":
                    # Organizers see their own events (all statuses) + published events from others
                    queryset = queryset.filter(
                        models.Q(organizer=user) | models.Q(status="published")
                    )
                elif user.user_type == "admin" or user.is_staff:
                    # Admins see everything
                    pass
                else:
                    # Regular users see only published
                    queryset = queryset.filter(status="published")
            else:
                # Anonymous users see only published
                queryset = queryset.filter(status="published")

        return queryset

    def perform_create(self, serializer):
        """Set organizer to current user"""
        serializer.save(organizer=self.request.user)

    @extend_schema(
        summary="Get organizer's events",
        description="Get all events created by the authenticated organizer",
        tags=["Events"],
    )
    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated, IsOrganizer]
    )
    def my_events(self, request):
        """Get all events created by the current organizer"""
        events = self.queryset.filter(organizer=request.user)
        serializer = EventListSerializer(
            events, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Get upcoming events",
        description="Get all upcoming published events",
        tags=["Events"],
    )
    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get upcoming events"""
        upcoming_events = self.queryset.filter(
            status="published", start_date__gt=timezone.now()
        ).order_by("start_date")
        serializer = EventListSerializer(
            upcoming_events, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Get featured events",
        description="Get all featured published events",
        tags=["Events"],
    )
    @action(detail=False, methods=["get"])
    def featured(self, request):
        """Get featured events"""
        featured_events = self.queryset.filter(
            status="published", is_featured=True
        ).order_by("-created_at")
        serializer = EventListSerializer(
            featured_events, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Publish event",
        description="Change event status to published (Owner only)",
        tags=["Events"],
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsEventOwner],
    )
    def publish(self, request, slug=None):
        """Publish an event"""
        event = self.get_object()

        if event.status == "published":
            return Response(
                {"message": "Event is already published"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.status = "published"
        event.published_at = timezone.now()
        event.save()

        serializer = EventDetailSerializer(event, context={"request": request})
        return Response(serializer.data)

    @extend_schema(
        summary="Cancel event",
        description="Cancel an event (Owner only)",
        tags=["Events"],
    )
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAuthenticated, IsEventOwner],
    )
    def cancel(self, request, slug=None):
        """Cancel an event"""
        event = self.get_object()

        if event.status == "cancelled":
            return Response(
                {"message": "Event is already cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if event.status == "completed":
            return Response(
                {"message": "Cannot cancel a completed event"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        event.status = "cancelled"
        event.save()

        serializer = EventDetailSerializer(event, context={"request": request})
        return Response(serializer.data)


# Import Q for queryset filtering
from django.db import models
