"""
Views for Tickets app using ViewSets
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
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import TicketType, TicketTier, DayPass
from .serializers import (
    TicketTypeListSerializer,
    TicketTypeDetailSerializer,
    TicketTypeCreateUpdateSerializer,
    TicketTierSerializer,
    DayPassSerializer,
)
from .permissions import IsEventOrganizer, IsEventOrganizerOrReadOnly
from Events.permissions import IsOrganizer


@extend_schema_view(
    list=extend_schema(
        summary="List all ticket types",
        description="Get a list of all ticket types with filtering",
        tags=["Tickets"],
        parameters=[
            OpenApiParameter(
                "event", OpenApiTypes.UUID, description="Filter by event ID"
            ),
            OpenApiParameter(
                "pricing_type", OpenApiTypes.STR, description="Filter by pricing type"
            ),
            OpenApiParameter(
                "is_active", OpenApiTypes.BOOL, description="Filter active tickets"
            ),
            OpenApiParameter(
                "is_on_sale", OpenApiTypes.BOOL, description="Filter tickets on sale"
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get ticket type details",
        description="Get detailed information about a specific ticket type including tiers and day passes",
        tags=["Tickets"],
    ),
    create=extend_schema(
        summary="Create new ticket type",
        description="Create a new ticket type for an event (Event organizer only)",
        tags=["Tickets"],
    ),
    update=extend_schema(
        summary="Update ticket type",
        description="Update an existing ticket type (Event organizer only)",
        tags=["Tickets"],
    ),
    partial_update=extend_schema(
        summary="Partially update ticket type",
        description="Partially update a ticket type (Event organizer only)",
        tags=["Tickets"],
    ),
    destroy=extend_schema(
        summary="Delete ticket type",
        description="Delete a ticket type (Event organizer only)",
        tags=["Tickets"],
    ),
)
class TicketTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ticket Types
    - List/Retrieve: Public access
    - Create/Update/Delete: Event organizer only
    """

    queryset = (
        TicketType.objects.select_related("event")
        .prefetch_related("tiers", "day_passes")
        .all()
    )
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["event", "pricing_type", "is_active"]
    search_fields = ["name", "description", "benefits"]
    ordering_fields = ["created_at", "price", "total_quantity"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == "list":
            return TicketTypeListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TicketTypeCreateUpdateSerializer
        return TicketTypeDetailSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        elif self.action == "create":
            return [IsAuthenticated(), IsOrganizer()]
        else:  # update, partial_update, destroy
            return [IsAuthenticated(), IsEventOrganizer()]

    def get_queryset(self):
        """Filter queryset based on query params"""
        queryset = super().get_queryset()

        # Filter by is_on_sale if provided
        is_on_sale = self.request.query_params.get("is_on_sale")
        if is_on_sale is not None:
            if is_on_sale.lower() == "true":
                # Filter tickets that are currently on sale
                queryset = [ticket for ticket in queryset if ticket.is_on_sale]
                queryset = TicketType.objects.filter(id__in=[t.id for t in queryset])

        return queryset

    @extend_schema(
        summary="Get tickets for an event",
        description="Get all ticket types for a specific event",
        tags=["Tickets"],
    )
    @action(detail=False, methods=["get"])
    def by_event(self, request):
        """Get all tickets for a specific event"""
        event_id = request.query_params.get("event_id")
        if not event_id:
            return Response(
                {"error": "event_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tickets = self.queryset.filter(event_id=event_id, is_active=True)
        serializer = TicketTypeListSerializer(
            tickets, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @extend_schema(
        summary="Get available tickets",
        description="Get all currently available tickets (on sale and not sold out)",
        tags=["Tickets"],
    )
    @action(detail=False, methods=["get"])
    def available(self, request):
        """Get all available tickets"""
        available_tickets = [ticket for ticket in self.queryset if ticket.is_on_sale]
        tickets = TicketType.objects.filter(id__in=[t.id for t in available_tickets])
        serializer = TicketTypeListSerializer(
            tickets, many=True, context={"request": request}
        )
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all ticket tiers",
        description="Get a list of all ticket tiers",
        tags=["Ticket Tiers"],
    ),
    retrieve=extend_schema(
        summary="Get tier details",
        description="Get detailed information about a specific tier",
        tags=["Ticket Tiers"],
    ),
    create=extend_schema(
        summary="Create new tier",
        description="Create a new ticket tier (Event organizer only)",
        tags=["Ticket Tiers"],
    ),
    update=extend_schema(
        summary="Update tier",
        description="Update an existing tier (Event organizer only)",
        tags=["Ticket Tiers"],
    ),
    partial_update=extend_schema(
        summary="Partially update tier",
        description="Partially update a tier (Event organizer only)",
        tags=["Ticket Tiers"],
    ),
    destroy=extend_schema(
        summary="Delete tier",
        description="Delete a tier (Event organizer only)",
        tags=["Ticket Tiers"],
    ),
)
class TicketTierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ticket Tiers
    Manages pricing tiers within ticket types
    """

    queryset = TicketTier.objects.select_related(
        "ticket_type", "ticket_type__event"
    ).all()
    serializer_class = TicketTierSerializer
    permission_classes = [IsEventOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["ticket_type"]
    ordering_fields = ["tier_number", "price"]
    ordering = ["tier_number"]


@extend_schema_view(
    list=extend_schema(
        summary="List all day passes",
        description="Get a list of all day passes",
        tags=["Day Passes"],
    ),
    retrieve=extend_schema(
        summary="Get day pass details",
        description="Get detailed information about a specific day pass",
        tags=["Day Passes"],
    ),
    create=extend_schema(
        summary="Create new day pass",
        description="Create a new day pass (Event organizer only)",
        tags=["Day Passes"],
    ),
    update=extend_schema(
        summary="Update day pass",
        description="Update an existing day pass (Event organizer only)",
        tags=["Day Passes"],
    ),
    partial_update=extend_schema(
        summary="Partially update day pass",
        description="Partially update a day pass (Event organizer only)",
        tags=["Day Passes"],
    ),
    destroy=extend_schema(
        summary="Delete day pass",
        description="Delete a day pass (Event organizer only)",
        tags=["Day Passes"],
    ),
)
class DayPassViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Day Passes
    Manages day-based tickets for multi-day events
    """

    queryset = DayPass.objects.select_related("ticket_type", "ticket_type__event").all()
    serializer_class = DayPassSerializer
    permission_classes = [IsEventOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["ticket_type", "is_all_days"]
    ordering_fields = ["day_number", "price", "date"]
    ordering = ["day_number"]
