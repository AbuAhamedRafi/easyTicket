"""
Common models for EasyTicket
Provides base models for consistent structure across all apps
"""

import uuid
from django.db import models


class BaseModelWithUID(models.Model):
    """
    Abstract base model that uses UUID as primary key
    All models should inherit from this for consistent structure
    """

    uid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier (UUID)",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
