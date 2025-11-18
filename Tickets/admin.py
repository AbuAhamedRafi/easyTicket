from django.contrib import admin
from .models import TicketType, TicketTier, DayPass, DayTierPrice, Ticket


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


class DayTierPriceInline(admin.TabularInline):
    """Inline for Day + Tier pricing combinations"""

    model = DayTierPrice
    extra = 1
    fields = [
        "day_number",
        "day_name",
        "date",
        "tier_number",
        "tier_name",
        "price",
        "quantity",
        "quantity_sold",
        "is_active",
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
    inlines = [TicketTierInline, DayPassInline, DayTierPriceInline]

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


@admin.register(DayTierPrice)
class DayTierPriceAdmin(admin.ModelAdmin):
    """Admin interface for Day + Tier pricing combinations"""

    list_display = [
        "ticket_type",
        "day_name",
        "tier_name",
        "price",
        "quantity",
        "quantity_sold",
        "available_quantity",
        "is_active",
        "is_on_sale",
    ]
    list_filter = ["is_active", "day_number", "tier_number", "date"]
    search_fields = ["day_name", "tier_name", "ticket_type__name"]
    readonly_fields = [
        "id",
        "quantity_sold",
        "available_quantity",
        "is_sold_out",
        "is_on_sale",
        "created_at",
        "updated_at",
    ]

    fieldsets = (
        (
            "Ticket Type",
            {"fields": ("id", "ticket_type")},
        ),
        (
            "Day Information",
            {
                "fields": (
                    "day_number",
                    "day_name",
                    "date",
                )
            },
        ),
        (
            "Tier Information",
            {
                "fields": (
                    "tier_number",
                    "tier_name",
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
            "Sales Period",
            {
                "fields": ("sales_start", "sales_end", "is_on_sale"),
                "classes": ("collapse",),
            },
        ),
        (
            "Status",
            {"fields": ("is_active",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("ticket_type", "ticket_type__event")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Admin interface for individual tickets"""

    list_display = [
        "ticket_number",
        "event",
        "ticket_name",
        "tier_name",
        "day_name",
        "status",
        "is_used",
        "attendee_name",
        "created_at",
    ]
    list_filter = [
        "status",
        "is_used",
        "event",
        "created_at",
    ]
    search_fields = [
        "ticket_number",
        "qr_code_data",
        "attendee_name",
        "attendee_email",
        "order_item__order__order_number",
    ]
    readonly_fields = [
        "id",
        "ticket_number",
        "qr_code_data",
        "order_item",
        "event",
        "ticket_type",
        "ticket_tier",
        "day_pass",
        "day_tier_price",
        "ticket_name",
        "tier_name",
        "day_name",
        "event_date",
        "price",
        "is_used",
        "used_at",
        "scanned_by",
        "created_at",
        "updated_at",
        "is_valid",
    ]

    fieldsets = (
        (
            "Ticket Information",
            {
                "fields": (
                    "id",
                    "ticket_number",
                    "qr_code_data",
                )
            },
        ),
        (
            "Order & Event Details",
            {
                "fields": (
                    "order_item",
                    "event",
                    "event_date",
                    "ticket_type",
                    "ticket_tier",
                    "day_pass",
                    "day_tier_price",
                )
            },
        ),
        (
            "Ticket Details",
            {
                "fields": (
                    "ticket_name",
                    "tier_name",
                    "day_name",
                    "price",
                )
            },
        ),
        (
            "Status & Verification",
            {
                "fields": (
                    "status",
                    "is_valid",
                    "is_used",
                    "used_at",
                    "scanned_by",
                )
            },
        ),
        (
            "Attendee Information",
            {
                "fields": (
                    "attendee_name",
                    "attendee_email",
                    "attendee_phone",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        """Prevent manual ticket creation - tickets are auto-generated"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent ticket deletion"""
        return request.user.is_superuser

    actions = ["mark_as_cancelled"]

    @admin.action(description="Mark selected tickets as cancelled")
    def mark_as_cancelled(self, request, queryset):
        """Bulk action to cancel tickets"""
        count = queryset.filter(status="active").update(status="cancelled")
        self.message_user(request, f"{count} tickets marked as cancelled.")
