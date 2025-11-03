"""
URL configuration for Events app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, EventCategoryViewSet

app_name = "events"

# Create router for viewsets
router = DefaultRouter()
router.register(r"categories", EventCategoryViewSet, basename="category")
router.register(r"", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]
