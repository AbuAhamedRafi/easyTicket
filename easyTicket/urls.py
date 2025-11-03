"""
URL configuration for easyTicket project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),
    # API routes
    path("api/auth/", include("UserAuth.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
admin.site.site_header = "EasyTicket Administration"
admin.site.site_title = "EasyTicket Admin"
admin.site.index_title = "Welcome to EasyTicket Admin Panel"
