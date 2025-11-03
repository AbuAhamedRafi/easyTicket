"""
Ticket models for EasyTicket
Supports tier-based pricing, day-based tickets, and combinations
"""

import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from Events.models import Event


class TicketType(models.Model):
    """
    Main ticket type for an event (e.g., VIP, General Admission, Early Bird)
    Can have multiple tiers or day passes
    """

    PRICING_TYPE_CHOICES = [
        ("simple", "Simple Pricing"),  # Single price
        ("tiered", "Tiered Pricing"),  # Tier 1, Tier 2, Tier 3
        ("day_based", "Day-Based Pricing"),  # Day 1, Day 2, All Days
        ("tier_and_day", "Tiered + Day-Based"),  # Combination
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
            # Get min from both tiers and days
            tier_prices = [t.price for t in self.tiers.all()]
            day_prices = [d.price for d in self.day_passes.all()]
            all_prices = tier_prices + day_prices
            return min(all_prices) if all_prices else 0
        return 0


class TicketTier(models.Model):
    """
    Pricing tiers for tickets (Tier 1: $50, Tier 2: $75, Tier 3: $100)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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


class DayPass(models.Model):
    """
    Day-based tickets for multi-day events (Day 1, Day 2, All Days)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
