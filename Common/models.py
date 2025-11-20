"""
Base models for the application
"""

import uuid
from django.db import models


class BaseModelWithUID(models.Model):
    """
    Abstract base model with UID primary key and timestamp fields
    All models should inherit from this for consistency
    """

    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Timestamp when this record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Timestamp when this record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.uid)
