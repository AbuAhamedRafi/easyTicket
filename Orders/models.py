"""
Order models for EasyTicket
Handles ticket purchases and order management
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from Events.models import Event
from Tickets.models import TicketType, TicketTier, DayPass


class Order(models.Model):
    """
    Main order model for ticket purchases
    """

    STATUS_CHOICES = [
        ("pending", "Pending"),  # Cart/created but not paid
        ("processing", "Processing"),  # Payment being processed
        ("confirmed", "Confirmed"),  # Payment successful, tickets issued
        ("cancelled", "Cancelled"),  # Order cancelled
        ("refunded", "Refunded"),  # Order refunded
        ("failed", "Failed"),  # Payment failed
    ]

    PAYMENT_METHOD_CHOICES = [
        ("stripe", "Stripe"),
        ("paypal", "PayPal"),
        ("card", "Credit/Debit Card"),
        ("bank_transfer", "Bank Transfer"),
        ("cash", "Cash"),
        ("pending", "Pending"),  # No payment method selected yet
    ]

    # Primary Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Human-readable order number (auto-generated)",
    )

    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="orders")

    # Order Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Pricing
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Total before fees and discounts",
    )
    service_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Platform service fee",
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(0)],
        help_text="Total discount applied",
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Final amount to be paid",
    )
    currency = models.CharField(max_length=3, default="USD")

    # Payment Information
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default="pending"
    )
    payment_id = models.CharField(
        max_length=255, blank=True, help_text="Payment gateway transaction ID"
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    # Customer Information
    buyer_email = models.EmailField()
    buyer_phone = models.CharField(max_length=20, blank=True)
    buyer_name = models.CharField(max_length=255, blank=True)

    # Promo/Discount
    promo_code = models.CharField(
        max_length=50, blank=True, help_text="Promo code applied (if any)"
    )

    # Notes & Metadata
    notes = models.TextField(blank=True, help_text="Customer notes or special requests")
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(
        null=True, blank=True, help_text="Pending orders expire after this time"
    )

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["event", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["order_number"]),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        """Auto-generate order number and calculate totals"""
        if not self.order_number:
            # Generate order number: OE-YYYYMMDD-XXXX
            from datetime import datetime

            date_str = datetime.now().strftime("%Y%m%d")
            # Get count of today's orders + 1
            today_start = timezone.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            count = Order.objects.filter(created_at__gte=today_start).count() + 1
            self.order_number = f"OE-{date_str}-{count:04d}"

        # Auto-calculate total if not set
        if not self.total_amount or self.total_amount == 0:
            self.total_amount = self.subtotal + self.service_fee - self.discount_amount

        # Set buyer info from user if not provided
        if not self.buyer_email:
            self.buyer_email = self.user.email
        if not self.buyer_name and (self.user.first_name or self.user.last_name):
            self.buyer_name = self.user.get_full_name()

        # Set expiry time for pending orders (30 minutes)
        if self.status == "pending" and not self.expires_at:
            from datetime import timedelta

            self.expires_at = timezone.now() + timedelta(minutes=30)

        super().save(*args, **kwargs)

    @property
    def is_paid(self):
        """Check if order is paid"""
        return self.status == "confirmed"

    @property
    def is_expired(self):
        """Check if pending order has expired"""
        if self.status == "pending" and self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def total_tickets(self):
        """Get total number of tickets in order"""
        return sum(item.quantity for item in self.items.all())

    def calculate_totals(self):
        """Recalculate order totals from items using consistent fee calculation"""
        from decimal import Decimal
        from django.conf import settings

        items = self.items.all()
        self.subtotal = sum(item.subtotal for item in items)

        # Use consistent service fee calculation from settings
        fee_percentage = Decimal(
            str(getattr(settings, "STRIPE_SERVICE_FEE_PERCENTAGE", 5.0))
        )
        self.service_fee = (self.subtotal * fee_percentage / Decimal("100")).quantize(
            Decimal("0.01")
        )

        # Apply discount if promo code is valid
        # (This would be implemented with a PromoCode model)

        self.total_amount = self.subtotal + self.service_fee - self.discount_amount
        self.save()

    def confirm_payment(self, payment_id=None, payment_method=None):
        """Mark order as confirmed after successful payment"""
        self.status = "confirmed"
        self.paid_at = timezone.now()
        if payment_id:
            self.payment_id = payment_id
        if payment_method:
            self.payment_method = payment_method
        self.save()

    def cancel_order(self, reason=""):
        """Cancel the order"""
        self.status = "cancelled"
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()


class OrderItem(models.Model):
    """
    Individual ticket items within an order
    Links to TicketType and optionally to TicketTier or DayPass
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    # Ticket Information
    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.PROTECT, related_name="order_items"
    )
    ticket_tier = models.ForeignKey(
        TicketTier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="order_items",
        help_text="Specific tier if tiered pricing",
    )
    day_pass = models.ForeignKey(
        DayPass,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="order_items",
        help_text="Specific day pass if day-based pricing",
    )

    # Quantity & Pricing (frozen at time of purchase)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)], default=1)
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per ticket at time of purchase",
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="quantity * unit_price",
    )

    # Ticket Details (snapshot at time of purchase)
    ticket_name = models.CharField(
        max_length=255, help_text="Ticket type name at time of purchase"
    )
    tier_name = models.CharField(
        max_length=100, blank=True, help_text="Tier name if applicable"
    )
    day_name = models.CharField(
        max_length=100, blank=True, help_text="Day pass name if applicable"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.quantity}x {self.ticket_name} - {self.order.order_number}"

    def save(self, *args, **kwargs):
        """Calculate subtotal and set ticket names"""
        # Calculate subtotal
        self.subtotal = self.quantity * self.unit_price

        # Set ticket names from related objects
        if not self.ticket_name:
            self.ticket_name = self.ticket_type.name
        if self.ticket_tier and not self.tier_name:
            self.tier_name = self.ticket_tier.name
        if self.day_pass and not self.day_name:
            self.day_name = self.day_pass.name

        super().save(*args, **kwargs)

    @property
    def full_ticket_name(self):
        """Get full ticket name with tier/day info"""
        name = self.ticket_name
        if self.tier_name:
            name += f" - {self.tier_name}"
        if self.day_name:
            name += f" - {self.day_name}"
        return name


class WebhookEvent(models.Model):
    """
    Track processed webhook events for idempotency
    Prevents duplicate processing of the same event
    """

    event_id = models.CharField(
        max_length=255, unique=True, db_index=True, help_text="Stripe event ID"
    )
    event_type = models.CharField(
        max_length=100, help_text="Event type (e.g., payment_intent.succeeded)"
    )
    processed_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField(
        null=True, blank=True, help_text="Event payload for debugging"
    )

    class Meta:
        verbose_name = "Webhook Event"
        verbose_name_plural = "Webhook Events"
        ordering = ["-processed_at"]
        indexes = [
            models.Index(fields=["event_id"]),
            models.Index(fields=["-processed_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.event_id}"
