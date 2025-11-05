"""
URL configuration for Tickets app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketTypeViewSet, TicketTierViewSet, DayPassViewSet, TicketViewSet

app_name = "tickets"

# Create router for viewsets
router = DefaultRouter()
router.register(r"types", TicketTypeViewSet, basename="ticket-type")
router.register(r"tiers", TicketTierViewSet, basename="ticket-tier")
router.register(r"day-passes", DayPassViewSet, basename="day-pass")
router.register(
    r"my-tickets", TicketViewSet, basename="my-tickets"
)  # User's individual tickets

urlpatterns = [
    path("", include(router.urls)),
]
