"""
Custom validators for input validation and security
"""

import re
import os
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class PhoneNumberValidator:
    """
    Validates phone number format
    Accepts international format: +1234567890 or 1234567890
    """

    message = "Invalid phone number format. Use format: +1234567890 or 1234567890"
    code = "invalid_phone"

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        if not value:  # Allow empty values (blank=True handles this)
            return

        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r"[\s\-\(\)]", "", value)

        # Validate format: optional +, then 9-15 digits
        phone_regex = re.compile(r"^\+?1?\d{9,15}$")
        if not phone_regex.match(cleaned):
            raise ValidationError(self.message, code=self.code)


validate_phone_number = PhoneNumberValidator()


@deconstructible
class ImageSizeValidator:
    """
    Validates that image file size is within limit
    """

    def __init__(self, max_size_mb=5):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024

    def __call__(self, image):
        if not image:
            return

        file_size = image.size
        if file_size > self.max_size_bytes:
            raise ValidationError(
                f"Image file size cannot exceed {self.max_size_mb}MB. "
                f"Current size: {file_size / (1024 * 1024):.2f}MB"
            )

    def __eq__(self, other):
        return (
            isinstance(other, ImageSizeValidator)
            and self.max_size_mb == other.max_size_mb
        )


@deconstructible
class ImageExtensionValidator:
    """
    Validates that image file has allowed extension
    """

    def __init__(self, allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = [".jpg", ".jpeg", ".png"]
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def __call__(self, image):
        if not image:
            return

        ext = os.path.splitext(image.name)[1].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f"Unsupported file extension '{ext}'. "
                f"Allowed extensions: {', '.join(self.allowed_extensions)}"
            )

    def __eq__(self, other):
        return (
            isinstance(other, ImageExtensionValidator)
            and self.allowed_extensions == other.allowed_extensions
        )


def validate_positive_decimal(value):
    """Validate that a decimal value is positive"""
    if value is not None and value < 0:
        raise ValidationError("Value must be positive")


def validate_not_in_past(value):
    """Validate that a date/datetime is not in the past"""
    from django.utils import timezone

    if value and value < timezone.now():
        raise ValidationError("Date cannot be in the past")


def validate_email_domain(value):
    """
    Validate email domain to prevent disposable email addresses
    Add your own blacklist of disposable email domains
    """
    if not value:
        return

    disposable_domains = [
        "tempmail.com",
        "throwaway.email",
        "guerrillamail.com",
        "10minutemail.com",
        "mailinator.com",
        "trashmail.com",
        # Add more as needed
    ]

    domain = value.split("@")[-1].lower()
    if domain in disposable_domains:
        raise ValidationError(
            f"Email from domain '{domain}' is not allowed. Please use a valid email address."
        )
