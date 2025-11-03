"""
URL configuration for Tickets app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketTypeViewSet, TicketTierViewSet, DayPassViewSet

app_name = "tickets"

# Create router for viewsets
router = DefaultRouter()
router.register(r"types", TicketTypeViewSet, basename="ticket-type")
router.register(r"tiers", TicketTierViewSet, basename="ticket-tier")
router.register(r"day-passes", DayPassViewSet, basename="day-pass")

urlpatterns = [
    path("", include(router.urls)),
]
