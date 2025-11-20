from django.contrib import admin
from .models import EventCategory, Event


@admin.register(EventCategory)
class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["uid", "created_at", "updated_at"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "organizer",
        "category",
        "pricing_type",
        "status",
        "start_date",
        "venue_city",
        "is_featured",
        "created_at",
    ]
    list_filter = [
        "status",
        "category",
        "pricing_type",
        "is_featured",
        "is_free",
        "start_date",
        "created_at",
    ]
    search_fields = ["title", "description", "venue_name", "venue_city", "tags"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["uid", "created_at", "updated_at", "published_at"]
    date_hierarchy = "start_date"

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "title",
                    "slug",
                    "description",
                    "short_description",
                    "category",
                    "tags",
                )
            },
        ),
        ("Organizer", {"fields": ("organizer",)}),
        (
            "Location",
            {
                "fields": (
                    "venue_name",
                    "venue_address",
                    "venue_city",
                    "venue_state",
                    "venue_country",
                    "venue_postal_code",
                    ("venue_latitude", "venue_longitude"),
                )
            },
        ),
        ("Date & Time", {"fields": ("start_date", "end_date")}),
        ("Media", {"fields": ("banner_image", "thumbnail_image")}),
        (
            "Capacity & Pricing",
            {
                "fields": (
                    "pricing_type",
                    "total_capacity",
                    "is_free",
                    "base_price",
                    "currency",
                )
            },
        ),
        ("Status & Visibility", {"fields": ("status", "is_featured", "published_at")}),
        (
            "Additional Details",
            {
                "fields": ("age_restriction", "terms_and_conditions", "refund_policy"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("organizer", "category")
