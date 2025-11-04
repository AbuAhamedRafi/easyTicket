"""
URL configuration for easyTicket project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # API routes
    path("api/auth/", include("UserAuth.urls")),
    path("api/events/", include("Events.urls")),
    path("api/tickets/", include("Tickets.urls")),
    path("api/orders/", include("Orders.urls")),
    path("api/", include("Orders.payment_urls")),  # Payment endpoints
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "EasyTicket Administration"
admin.site.site_title = "EasyTicket Admin"
admin.site.index_title = "Welcome to EasyTicket Admin Panel"
