from django.contrib import admin
from .models import TicketType, TicketTier, DayPass


class TicketTierInline(admin.TabularInline):
    model = TicketTier
    extra = 1
    fields = [
        "tier_number",
        "name",
        "price",
        "quantity",
        "quantity_sold",
        "sales_start",
        "sales_end",
    ]
    readonly_fields = ["quantity_sold"]


class DayPassInline(admin.TabularInline):
    model = DayPass
    extra = 1
    fields = [
        "day_number",
        "name",
        "date",
        "price",
        "quantity",
        "quantity_sold",
        "is_all_days",
    ]
    readonly_fields = ["quantity_sold"]


@admin.register(TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "event",
        "pricing_type",
        "price",
        "total_quantity",
        "quantity_sold",
        "available_quantity",
        "is_active",
        "is_on_sale",
    ]
    list_filter = ["pricing_type", "is_active", "created_at"]
    search_fields = ["name", "description", "event__title"]
    readonly_fields = [
        "id",
        "quantity_sold",
        "available_quantity",
        "is_sold_out",
        "is_on_sale",
        "min_price",
        "created_at",
        "updated_at",
    ]
    inlines = [TicketTierInline, DayPassInline]

    fieldsets = (
        ("Basic Information", {"fields": ("id", "event", "name", "description")}),
        ("Pricing", {"fields": ("pricing_type", "price", "min_price")}),
        (
            "Inventory",
            {
                "fields": (
                    "total_quantity",
                    "quantity_sold",
                    "available_quantity",
                    "is_sold_out",
                )
            },
        ),
        ("Sales Period", {"fields": ("sales_start", "sales_end", "is_on_sale")}),
        ("Purchase Limits", {"fields": ("min_purchase", "max_purchase")}),
        (
            "Additional Details",
            {"fields": ("benefits", "is_active"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("event")


@admin.register(TicketTier)
class TicketTierAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "ticket_type",
        "tier_number",
        "price",
        "quantity",
        "quantity_sold",
        "available_quantity",
        "is_sold_out",
    ]
    list_filter = ["tier_number", "created_at"]
    search_fields = ["name", "ticket_type__name"]
    readonly_fields = [
        "id",
        "quantity_sold",
        "available_quantity",
        "is_sold_out",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        ("Basic Information", {"fields": ("id", "ticket_type", "tier_number", "name")}),
        ("Pricing", {"fields": ("price",)}),
        (
            "Inventory",
            {
                "fields": (
                    "quantity",
                    "quantity_sold",
                    "available_quantity",
                    "is_sold_out",
                )
            },
        ),
        (
            "Sales Period",
            {"fields": ("sales_start", "sales_end"), "classes": ("collapse",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(DayPass)
class DayPassAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "ticket_type",
        "day_number",
        "date",
        "price",
        "quantity",
        "quantity_sold",
        "available_quantity",
        "is_all_days",
        "is_sold_out",
    ]
    list_filter = ["is_all_days", "date", "created_at"]
    search_fields = ["name", "ticket_type__name"]
    readonly_fields = [
        "id",
        "quantity_sold",
        "available_quantity",
        "is_sold_out",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "ticket_type",
                    "day_number",
                    "name",
                    "date",
                    "is_all_days",
                )
            },
        ),
        ("Pricing", {"fields": ("price",)}),
        (
            "Inventory",
            {
                "fields": (
                    "quantity",
                    "quantity_sold",
                    "available_quantity",
                    "is_sold_out",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
