"""
Ticket models for EasyTicket
Supports tier-based pricing, day-based tickets, and combinations
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from Common.models import BaseModelWithUID
from Events.models import Event


class TicketType(BaseModelWithUID):
    """
    Main ticket type for an event (e.g., VIP, General Admission, Early Bird)
    Can have multiple tiers or day passes
    """

    PRICING_TYPE_CHOICES = [
        ("simple", "Simple Pricing"),  # Single ticket type with one price
        ("tiered", "Tiered Pricing"),  # Multiple tiers (VIP, General, etc.)
        ("day_based", "Day-Based Pricing"),  # Multiple days (Day 1, Day 2, All Days)
        ("tier_and_day", "Tiered + Day-Based"),  # Matrix: Each day has multiple tiers
    ]

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="ticket_types"
    )

    # Basic Information
    name = models.CharField(
        max_length=100, help_text="E.g., VIP Pass, General Admission, Early Bird"
    )
    description = models.TextField(blank=True)

    # Pricing Configuration
    pricing_type = models.CharField(
        max_length=20, choices=PRICING_TYPE_CHOICES, default="simple"
    )

    # For simple pricing only
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        help_text="Used only for simple pricing type",
    )

    # Availability
    total_quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Total tickets available for this type",
    )
    quantity_sold = models.PositiveIntegerField(
        default=0, help_text="Number of tickets sold"
    )

    # Sales Period
    sales_start = models.DateTimeField(
        null=True, blank=True, help_text="When ticket sales begin (optional)"
    )
    sales_end = models.DateTimeField(
        null=True, blank=True, help_text="When ticket sales end (optional)"
    )

    # Features & Restrictions
    min_purchase = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Minimum tickets per purchase",
    )
    max_purchase = models.PositiveIntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Maximum tickets per purchase",
    )

    benefits = models.TextField(
        blank=True, help_text="Special benefits/perks (e.g., VIP lounge access, merch)"
    )

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Ticket Type"
        verbose_name_plural = "Ticket Types"
        ordering = ["event", "created_at"]
        unique_together = [["event", "name"]]

    def __str__(self):
        return f"{self.event.title} - {self.name}"

    @property
    def available_quantity(self):
        """Get number of available tickets"""
        return max(0, self.total_quantity - self.quantity_sold)

    @property
    def is_sold_out(self):
        """Check if tickets are sold out"""
        return self.available_quantity == 0

    @property
    def is_on_sale(self):
        """Check if tickets are currently on sale"""
        now = timezone.now()

        if not self.is_active:
            return False

        if self.is_sold_out:
            return False

        if self.sales_start and now < self.sales_start:
            return False

        if self.sales_end and now > self.sales_end:
            return False

        return True

    @property
    def min_price(self):
        """Get minimum price for this ticket type"""
        if self.pricing_type == "simple":
            return self.price
        elif self.pricing_type == "tiered":
            tiers = self.tiers.all()
            return min([t.price for t in tiers]) if tiers else 0
        elif self.pricing_type == "day_based":
            days = self.day_passes.all()
            return min([d.price for d in days]) if days else 0
        elif self.pricing_type == "tier_and_day":
            # Get min from day_tier_prices (the combination matrix)
            day_tier_prices = self.day_tier_prices.all()
            return min([dt.price for dt in day_tier_prices]) if day_tier_prices else 0
        return 0


class TicketTier(BaseModelWithUID):
    """
    Pricing tiers for tickets (Tier 1: $50, Tier 2: $75, Tier 3: $100)
    """

    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, related_name="tiers"
    )

    tier_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Tier level (1 = cheapest, higher = more expensive)",
    )
    name = models.CharField(max_length=50, help_text="E.g., Tier 1, Tier 2, Early Bird")
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Tier-specific quantity
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], help_text="Number of tickets in this tier"
    )
    quantity_sold = models.PositiveIntegerField(default=0)

    # Tier-specific sales period (optional, overrides ticket_type dates)
    sales_start = models.DateTimeField(null=True, blank=True)
    sales_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Ticket Tier"
        verbose_name_plural = "Ticket Tiers"
        ordering = ["ticket_type", "tier_number"]
        unique_together = [["ticket_type", "tier_number"], ["ticket_type", "name"]]

    def __str__(self):
        return f"{self.ticket_type.name} - {self.name}"

    @property
    def available_quantity(self):
        return max(0, self.quantity - self.quantity_sold)

    @property
    def is_sold_out(self):
        return self.available_quantity == 0


class DayPass(BaseModelWithUID):
    """
    Day-based tickets for multi-day events (Day 1, Day 2, All Days)
    Used for 'day_based' pricing type only
    For 'tier_and_day' pricing, use DayTierPrice model instead
    """

    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, related_name="day_passes"
    )

    day_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Day number (null for All Days pass)",
    )
    name = models.CharField(
        max_length=50, help_text="E.g., Day 1, Day 2, All Days Pass"
    )
    date = models.DateField(
        null=True, blank=True, help_text="Specific date for this day pass"
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    # Day-specific quantity
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of passes available for this day",
    )
    quantity_sold = models.PositiveIntegerField(default=0)

    is_all_days = models.BooleanField(
        default=False, help_text="True if this is an 'All Days' pass"
    )

    class Meta:
        verbose_name = "Day Pass"
        verbose_name_plural = "Day Passes"
        ordering = ["ticket_type", "day_number"]
        unique_together = [["ticket_type", "day_number"], ["ticket_type", "name"]]

    def __str__(self):
        return f"{self.ticket_type.name} - {self.name}"

    @property
    def available_quantity(self):
        return max(0, self.quantity - self.quantity_sold)

    @property
    def is_sold_out(self):
        return self.available_quantity == 0


class DayTierPrice(BaseModelWithUID):
    """
    Combination of Day + Tier pricing for multi-day events with tier levels
    Used ONLY for 'tier_and_day' pricing type

    Example Structure:
    - Day 1 + VIP (Tier 1) = $150
    - Day 1 + General (Tier 2) = $75
    - Day 2 + VIP (Tier 1) = $150
    - Day 2 + General (Tier 2) = $75
    """

    ticket_type = models.ForeignKey(
        TicketType, on_delete=models.CASCADE, related_name="day_tier_prices"
    )

    # Day Information
    day_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], help_text="Day number (1, 2, 3, etc.)"
    )
    day_name = models.CharField(
        max_length=50, help_text="E.g., Day 1, Day 2, Friday, Saturday"
    )
    date = models.DateField(
        null=True, blank=True, help_text="Specific date for this day"
    )

    # Tier Information
    tier_number = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Tier level (1 = VIP/highest, 2 = General, etc.)",
    )
    tier_name = models.CharField(
        max_length=50, help_text="E.g., VIP, General Admission, Regular"
    )

    # Pricing
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price for this Day + Tier combination",
    )

    # Availability
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of tickets available for this Day + Tier combination",
    )
    quantity_sold = models.PositiveIntegerField(
        default=0, help_text="Number sold for this combination"
    )

    # Sales Period (optional, overrides ticket_type dates)
    sales_start = models.DateTimeField(null=True, blank=True)
    sales_end = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(
        default=True, help_text="Is this combination currently available?"
    )

    class Meta:
        verbose_name = "Day + Tier Price"
        verbose_name_plural = "Day + Tier Prices"
        ordering = ["ticket_type", "day_number", "tier_number"]
        unique_together = [
            ["ticket_type", "day_number", "tier_number"],
            ["ticket_type", "day_name", "tier_name"],
        ]
        indexes = [
            models.Index(fields=["ticket_type", "day_number", "tier_number"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.ticket_type.name} - {self.day_name} - {self.tier_name}"

    @property
    def available_quantity(self):
        """Get number of available tickets for this combination"""
        return max(0, self.quantity - self.quantity_sold)

    @property
    def is_sold_out(self):
        """Check if this Day+Tier combination is sold out"""
        return self.available_quantity == 0

    @property
    def is_on_sale(self):
        """Check if this Day+Tier combination is currently on sale"""
        if not self.is_active:
            return False

        if self.is_sold_out:
            return False

        now = timezone.now()

        if self.sales_start and now < self.sales_start:
            return False

        if self.sales_end and now > self.sales_end:
            return False

        return True


class Ticket(BaseModelWithUID):
    """
    Individual ticket instance with unique QR code
    Generated when order is confirmed
    """

    STATUS_CHOICES = [
        ("active", "Active"),  # Valid, not yet used
        ("used", "Used"),  # Scanned and used at event
        ("cancelled", "Cancelled"),  # Order cancelled/refunded
        ("expired", "Expired"),  # Event date passed
    ]

    # Primary fields
    ticket_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        help_text="Human-readable ticket number (auto-generated)",
    )

    # Relationships
    order_item = models.ForeignKey(
        "Orders.OrderItem",
        on_delete=models.CASCADE,
        related_name="tickets",
        help_text="The order item this ticket belongs to",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="tickets",
        help_text="Event this ticket is for",
    )
    ticket_type = models.ForeignKey(
        TicketType,
        on_delete=models.PROTECT,
        related_name="tickets",
        help_text="Type of ticket",
    )

    # Pricing Model References (only ONE will be set based on pricing_type)
    ticket_tier = models.ForeignKey(
        TicketTier,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
        help_text="For 'tiered' pricing: Specific tier (VIP, General, etc.)",
    )
    day_pass = models.ForeignKey(
        DayPass,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
        help_text="For 'day_based' pricing: Specific day pass",
    )
    day_tier_price = models.ForeignKey(
        "DayTierPrice",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="tickets",
        help_text="For 'tier_and_day' pricing: Specific Day+Tier combination",
    )

    # Ticket Details (snapshot at time of creation)
    ticket_name = models.CharField(
        max_length=255, help_text="Ticket type name at time of creation"
    )
    tier_name = models.CharField(
        max_length=100, blank=True, help_text="Tier name if applicable"
    )
    day_name = models.CharField(
        max_length=100, blank=True, help_text="Day pass name if applicable"
    )
    event_date = models.DateTimeField(help_text="Event date/time (snapshot)")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price paid for this ticket",
    )

    # QR Code
    qr_code_data = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="Unique QR code data for verification",
    )

    # Status & Verification
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    is_used = models.BooleanField(default=False, help_text="Has ticket been scanned?")
    used_at = models.DateTimeField(
        null=True, blank=True, help_text="When ticket was scanned"
    )
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scanned_tickets",
        help_text="Staff member who scanned ticket",
    )

    # Attendee Information (optional)
    attendee_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of person attending with this ticket",
    )
    attendee_email = models.EmailField(
        blank=True, help_text="Email of person attending"
    )
    attendee_phone = models.CharField(
        max_length=15, blank=True, help_text="Phone of person attending"
    )

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ticket_number"]),
            models.Index(fields=["qr_code_data"]),
            models.Index(fields=["event", "status"]),
            models.Index(fields=["order_item"]),
        ]

    def __str__(self):
        return f"{self.ticket_number} - {self.ticket_name}"

    def save(self, *args, **kwargs):
        """Auto-generate ticket number and QR code data"""
        if not self.ticket_number:
            # Generate ticket number: TKT-YYYYMMDD-XXXX
            from datetime import datetime

            date_str = datetime.now().strftime("%Y%m%d")
            # Get count of today's tickets + 1
            today_start = timezone.now().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            count = Ticket.objects.filter(created_at__gte=today_start).count() + 1
            self.ticket_number = f"TKT-{date_str}-{count:05d}"

        if not self.qr_code_data:
            # Generate unique QR code data combining ticket ID and secret
            import hashlib

            secret = f"{self.id}{self.ticket_number}{timezone.now().isoformat()}"
            self.qr_code_data = hashlib.sha256(secret.encode()).hexdigest()

        # Set ticket details from related objects if not set
        if not self.ticket_name:
            self.ticket_name = self.ticket_type.name

        # Handle different pricing types
        if self.ticket_tier and not self.tier_name:
            self.tier_name = self.ticket_tier.name
        if self.day_pass and not self.day_name:
            self.day_name = self.day_pass.name
        if self.day_tier_price:
            # For tier_and_day pricing, extract both tier and day info
            if not self.tier_name:
                self.tier_name = self.day_tier_price.tier_name
            if not self.day_name:
                self.day_name = self.day_tier_price.day_name

        if not self.event_date:
            self.event_date = self.event.start_date

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

    @property
    def is_valid(self):
        """Check if ticket is valid for use"""
        if self.status != "active":
            return False
        if self.is_used:
            return False
        # Check if event hasn't ended yet
        if self.event.end_date and timezone.now() > self.event.end_date:
            return False
        return True

    def mark_as_used(self, scanned_by_user=None):
        """Mark ticket as used/scanned"""
        self.is_used = True
        self.used_at = timezone.now()
        self.status = "used"
        if scanned_by_user:
            self.scanned_by = scanned_by_user
        self.save(update_fields=["is_used", "used_at", "status", "scanned_by"])

    def cancel(self):
        """Cancel ticket (e.g., when order is refunded)"""
        self.status = "cancelled"
        self.save(update_fields=["status"])
