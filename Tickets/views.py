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
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import TicketType, TicketTier, DayPass, DayTierPrice, Ticket
from .serializers import (
    TicketTypeListSerializer,
    TicketTypeDetailSerializer,
    TicketTypeCreateUpdateSerializer,
    TicketTierSerializer,
    DayPassSerializer,
    DayTierPriceSerializer,
    TicketSerializer,
    TicketVerificationSerializer,
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
        .prefetch_related("tiers", "day_passes", "day_tier_prices")
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
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
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
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
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


@extend_schema_view(
    list=extend_schema(
        summary="List all day+tier prices",
        description="Get a list of all day and tier price combinations",
        tags=["Day Tier Prices"],
    ),
    retrieve=extend_schema(
        summary="Get day+tier price details",
        description="Get detailed information about a specific day+tier price combination",
        tags=["Day Tier Prices"],
    ),
    create=extend_schema(
        summary="Create new day+tier price",
        description="Create a new day+tier price combination (Event organizer only)",
        tags=["Day Tier Prices"],
    ),
    update=extend_schema(
        summary="Update day+tier price",
        description="Update an existing day+tier price (Event organizer only)",
        tags=["Day Tier Prices"],
    ),
    partial_update=extend_schema(
        summary="Partially update day+tier price",
        description="Partially update a day+tier price (Event organizer only)",
        tags=["Day Tier Prices"],
    ),
    destroy=extend_schema(
        summary="Delete day+tier price",
        description="Delete a day+tier price (Event organizer only)",
        tags=["Day Tier Prices"],
    ),
)
class DayTierPriceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Day + Tier Price Combinations
    Manages pricing matrix for multi-day tiered events
    """

    queryset = DayTierPrice.objects.select_related(
        "ticket_type", "ticket_type__event"
    ).all()
    serializer_class = DayTierPriceSerializer
    permission_classes = [IsEventOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["ticket_type", "day_number", "tier_number", "is_active"]
    ordering_fields = ["day_number", "tier_number", "price", "date"]
    ordering = ["day_number", "tier_number"]

    @extend_schema(
        summary="Get pricing matrix",
        description="Get the full Day×Tier pricing matrix for a ticket type",
        tags=["Day Tier Prices"],
        parameters=[
            OpenApiParameter(
                "ticket_type",
                OpenApiTypes.UUID,
                description="Filter by ticket type ID",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def matrix(self, request):
        """
        Get pricing matrix for a ticket type
        Returns data organized by day and tier

        GET /api/tickets/day-tier-prices/matrix/?ticket_type=<uuid>
        """
        ticket_type_id = request.query_params.get("ticket_type")
        if not ticket_type_id:
            return Response(
                {"error": "ticket_type parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get all day+tier prices for this ticket type
        day_tier_prices = self.queryset.filter(
            ticket_type_id=ticket_type_id, is_active=True
        ).order_by("day_number", "tier_number")

        # Organize into matrix structure
        matrix = {}
        days = set()
        tiers = set()

        for dtp in day_tier_prices:
            days.add((dtp.day_number, dtp.day_name))
            tiers.add((dtp.tier_number, dtp.tier_name))

            if dtp.day_number not in matrix:
                matrix[dtp.day_number] = {}

            matrix[dtp.day_number][dtp.tier_number] = DayTierPriceSerializer(dtp).data

        # Format response
        response_data = {
            "ticket_type": ticket_type_id,
            "days": sorted(
                [{"number": d[0], "name": d[1]} for d in days],
                key=lambda x: x["number"],
            ),
            "tiers": sorted(
                [{"number": t[0], "name": t[1]} for t in tiers],
                key=lambda x: x["number"],
            ),
            "matrix": matrix,
        }

        return Response(response_data)


# ==================== Individual Ticket ViewSet ====================


@extend_schema_view(
    list=extend_schema(
        summary="List user's tickets",
        description="Get all tickets for the authenticated user",
        tags=["My Tickets"],
    ),
    retrieve=extend_schema(
        summary="Get ticket details",
        description="Get detailed information about a specific ticket",
        tags=["My Tickets"],
    ),
)
class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for individual user tickets
    - List: Get all tickets for authenticated user
    - Retrieve: Get details of a specific ticket
    - verify: Verify and scan a ticket (staff/organizer only)
    """

    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["status", "is_used", "event"]
    ordering_fields = ["created_at", "event_date"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Get tickets for current user (or all for staff)"""
        user = self.request.user

        if user.is_staff or user.user_type == "organizer":
            # Staff and organizers can see all tickets (filtered by their events)
            return Ticket.objects.select_related(
                "event",
                "ticket_type",
                "ticket_tier",
                "day_pass",
                "day_tier_price",
                "order_item__order",
            ).all()

        # Regular users see only their tickets
        return Ticket.objects.filter(order_item__order__user=user).select_related(
            "event",
            "ticket_type",
            "ticket_tier",
            "day_pass",
            "day_tier_price",
            "order_item__order",
        )

    @extend_schema(
        summary="Verify and scan ticket",
        description="Verify a ticket's QR code and mark it as used. Staff/Organizer only.",
        tags=["Ticket Verification"],
        request=TicketVerificationSerializer,
        responses={200: TicketSerializer, 400: dict},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def verify(self, request):
        """
        Verify a ticket via QR code scan

        POST /api/tickets/verify/
        Body: {"qr_code_data": "hash..."}

        Returns ticket details if valid
        Marks ticket as used if successful
        """
        # Only staff and organizers can scan tickets
        if not (request.user.is_staff or request.user.user_type == "organizer"):
            return Response(
                {"error": "Only staff and event organizers can scan tickets"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TicketVerificationSerializer(
            data=request.data, context={"scanner": request.user}
        )

        if serializer.is_valid():
            # Mark ticket as used
            ticket = serializer.save()

            # Return ticket details
            return Response(
                {
                    "success": True,
                    "message": "Ticket verified and marked as used",
                    "ticket": TicketSerializer(ticket).data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            # Return validation errors
            return Response(
                {
                    "success": False,
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="Get ticket statistics",
        description="Get statistics about user's tickets",
        tags=["My Tickets"],
    )
    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get ticket statistics for user"""
        user = request.user
        tickets = Ticket.objects.filter(order_item__order__user=user)

        stats = {
            "total_tickets": tickets.count(),
            "active_tickets": tickets.filter(status="active", is_used=False).count(),
            "used_tickets": tickets.filter(is_used=True).count(),
            "cancelled_tickets": tickets.filter(status="cancelled").count(),
            "upcoming_events": tickets.filter(
                status="active", is_used=False, event__start_date__gte=timezone.now()
            )
            .values_list("event", flat=True)
            .distinct()
            .count(),
        }

        return Response(stats)

    ordering = ["day_number"]
