"""
Management command to auto-cancel orders that have been pending for too long
Run every 5 minutes via cron: */5 * * * * python manage.py cancel_expired_orders
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from Orders.models import Order
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Cancel orders that have been pending for more than specified minutes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--minutes",
            type=int,
            default=30,
            help="Number of minutes after which pending orders expire (default: 30)",
        )

    def handle(self, *args, **options):
        minutes = options["minutes"]
        cutoff = timezone.now() - timedelta(minutes=minutes)

        # Find expired pending orders
        expired_orders = Order.objects.filter(status="pending", created_at__lt=cutoff)

        count = 0
        for order in expired_orders:
            order.status = "cancelled"
            order.cancellation_reason = (
                f"Automatic cancellation - payment timeout ({minutes} minutes)"
            )
            order.cancelled_at = timezone.now()
            order.save()
            count += 1
            logger.info(
                f"Auto-cancelled expired order: {order.order_number} "
                f"(created: {order.created_at})"
            )

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired orders found"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully cancelled {count} expired orders")
            )
