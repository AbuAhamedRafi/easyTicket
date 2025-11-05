"""
Management command to cleanup expired email verification tokens
Run daily via cron: 0 2 * * * python manage.py cleanup_tokens
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from UserAuth.models import User


class Command(BaseCommand):
    help = "Cleanup expired email verification tokens (older than 24 hours)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=24,
            help="Number of hours after which tokens expire (default: 24)",
        )

    def handle(self, *args, **options):
        hours = options["hours"]
        cutoff = timezone.now() - timedelta(hours=hours)

        # Find users with expired tokens
        expired = User.objects.filter(
            email_verification_token__isnull=False,
            email_verification_token_created__lt=cutoff,
        )

        count = expired.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired tokens found"))
            return

        # Clear expired tokens
        expired.update(
            email_verification_token=None, email_verification_token_created=None
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleaned up {count} expired verification tokens"
            )
        )
