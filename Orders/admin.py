"""
Admin configuration for Orders app
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, WebhookEvent


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""

    model = OrderItem
    extra = 0
    readonly_fields = ["subtotal", "created_at"]
    fields = [
        "ticket_type",
        "ticket_tier",
        "day_pass",
        "day_tier_price",
        "quantity",
        "unit_price",
        "subtotal",
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for Order model"""

    list_display = [
        "order_number",
        "user_email",
        "event_title",
        "status_badge",
        "total_amount",
        "total_tickets_count",
        "payment_method",
        "created_at",
    ]

    list_filter = [
        "status",
        "payment_method",
        "created_at",
        "paid_at",
    ]

    search_fields = [
        "order_number",
        "user__email",
        "event__title",
        "buyer_email",
        "buyer_name",
        "payment_id",
    ]

    readonly_fields = [
        "uid",
        "order_number",
        "created_at",
        "updated_at",
        "paid_at",
        "cancelled_at",
        "total_tickets",
        "is_paid",
        "is_expired",
    ]

    fieldsets = [
        (
            "Order Information",
            {
                "fields": [
                    "uid",
                    "order_number",
                    "user",
                    "event",
                    "status",
                ]
            },
        ),
        (
            "Pricing",
            {
                "fields": [
                    "subtotal",
                    "service_fee",
                    "discount_amount",
                    "total_amount",
                    "currency",
                ]
            },
        ),
        (
            "Payment",
            {
                "fields": [
                    "payment_method",
                    "payment_id",
                    "paid_at",
                ]
            },
        ),
        (
            "Buyer Information",
            {
                "fields": [
                    "buyer_email",
                    "buyer_phone",
                    "buyer_name",
                ]
            },
        ),
        (
            "Additional Details",
            {
                "fields": [
                    "promo_code",
                    "notes",
                    "cancellation_reason",
                    "cancelled_at",
                ]
            },
        ),
        (
            "Metadata",
            {
                "fields": [
                    "created_at",
                    "updated_at",
                    "expires_at",
                    "total_tickets",
                    "is_paid",
                    "is_expired",
                ]
            },
        ),
    ]

    inlines = [OrderItemInline]

    def user_email(self, obj):
        """Display user email"""
        return obj.user.email

    user_email.short_description = "User"
    user_email.admin_order_field = "user__email"

    def event_title(self, obj):
        """Display event title"""
        return obj.event.title

    event_title.short_description = "Event"
    event_title.admin_order_field = "event__title"

    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            "pending": "#FFA500",  # Orange
            "processing": "#0000FF",  # Blue
            "confirmed": "#008000",  # Green
            "cancelled": "#808080",  # Gray
            "refunded": "#800080",  # Purple
            "failed": "#FF0000",  # Red
        }
        color = colors.get(obj.status, "#000000")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Status"
    status_badge.admin_order_field = "status"

    def total_tickets_count(self, obj):
        """Display total tickets in order"""
        return obj.total_tickets

    total_tickets_count.short_description = "Tickets"

    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related("user", "event").prefetch_related("items")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for OrderItem model"""

    list_display = [
        "order_number",
        "full_ticket_name",
        "quantity",
        "unit_price",
        "subtotal",
        "created_at",
    ]

    list_filter = [
        "created_at",
        "ticket_type",
    ]

    search_fields = [
        "order__order_number",
        "ticket_name",
        "tier_name",
        "day_name",
    ]

    readonly_fields = [
        "uid",
        "subtotal",
        "full_ticket_name",
        "created_at",
        "updated_at",
    ]

    fieldsets = [
        ("Order", {"fields": ["order"]}),
        (
            "Ticket Information",
            {
                "fields": [
                    "ticket_type",
                    "ticket_tier",
                    "day_pass",
                    "day_tier_price",
                    "ticket_name",
                    "tier_name",
                    "day_name",
                    "full_ticket_name",
                ]
            },
        ),
        (
            "Pricing",
            {
                "fields": [
                    "quantity",
                    "unit_price",
                    "subtotal",
                ]
            },
        ),
        (
            "Metadata",
            {
                "fields": [
                    "uid",
                    "created_at",
                    "updated_at",
                ]
            },
        ),
    ]

    def order_number(self, obj):
        """Display order number"""
        return obj.order.order_number

    order_number.short_description = "Order"
    order_number.admin_order_field = "order__order_number"

    def get_queryset(self, request):
        """Optimize queries"""
        qs = super().get_queryset(request)
        return qs.select_related(
            "order", "ticket_type", "ticket_tier", "day_pass", "day_tier_price"
        )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Admin for WebhookEvent model"""

    list_display = [
        "event_id",
        "event_type",
        "processed_at",
    ]

    list_filter = [
        "event_type",
        "processed_at",
    ]

    search_fields = [
        "event_id",
        "event_type",
    ]

    readonly_fields = [
        "event_id",
        "event_type",
        "processed_at",
        "payload",
    ]

    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent editing"""
        return False
