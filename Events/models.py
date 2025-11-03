"""
Event models for EasyTicket
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class EventCategory(models.Model):
    """
    Categories for events (Music, Sports, Conference, etc.)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class or emoji")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Category"
        verbose_name_plural = "Event Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(models.Model):
    """
    Event model for managing events created by organizers
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    short_description = models.CharField(
        max_length=500, blank=True, help_text="Brief description for listings"
    )

    # Relationships
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_events",
        limit_choices_to={"user_type": "organizer"},
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    # Location & Timing
    venue_name = models.CharField(max_length=255)
    venue_address = models.TextField()
    venue_city = models.CharField(max_length=100)
    venue_state = models.CharField(max_length=100, blank=True)
    venue_country = models.CharField(max_length=100)
    venue_postal_code = models.CharField(max_length=20, blank=True)
    venue_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="For map integration",
    )
    venue_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="For map integration",
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Media
    banner_image = models.ImageField(
        upload_to="events/banners/%Y/%m/", null=True, blank=True
    )
    thumbnail_image = models.ImageField(
        upload_to="events/thumbnails/%Y/%m/", null=True, blank=True
    )

    # Capacity & Status
    total_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], help_text="Total number of attendees allowed"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # Pricing (base price, actual pricing handled by Tickets app)
    is_free = models.BooleanField(default=False)
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        help_text="Starting price (if not free)",
    )
    currency = models.CharField(max_length=3, default="USD")

    # Additional Information
    terms_and_conditions = models.TextField(blank=True)
    refund_policy = models.TextField(blank=True)
    age_restriction = models.PositiveIntegerField(
        null=True, blank=True, help_text="Minimum age requirement (e.g., 18)"
    )

    # SEO & Marketing
    tags = models.CharField(
        max_length=500, blank=True, help_text="Comma-separated tags for search"
    )
    is_featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-start_date"]
        indexes = [
            models.Index(fields=["-start_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["organizer"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Auto-generate slug and set published_at"""
        if not self.slug:
            from django.utils.text import slugify

            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Set published_at when status changes to published
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        """Check if event hasn't started yet"""
        return self.start_date > timezone.now()

    @property
    def is_ongoing(self):
        """Check if event is currently happening"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    @property
    def is_past(self):
        """Check if event has ended"""
        return self.end_date < timezone.now()

    @property
    def duration_days(self):
        """Calculate event duration in days"""
        return (self.end_date - self.start_date).days

    def get_available_tickets_count(self):
        """Get number of available tickets (to be implemented with Tickets app)"""
        # TODO: Implement when Tickets app is created
        return self.total_capacity
