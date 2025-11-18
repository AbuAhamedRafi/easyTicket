"""
Signals for Orders app
Handles ticket inventory updates and ticket generation when orders are confirmed/cancelled
"""

from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
import logging

from .models import Order, OrderItem

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def track_order_status_change(sender, instance, **kwargs):
    """
    Track the old status before saving to detect status changes
    """
    if instance.pk:  # Only for existing orders
        try:
            old_instance = Order.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Order.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Order)
def update_ticket_inventory_on_order_save(sender, instance, created, **kwargs):
    """
    Update ticket inventory when order status changes
    - When order is confirmed: increase quantity_sold
    - When order is cancelled/failed: decrease quantity_sold (restore inventory)
    """
    # Skip if this is a new order being created
    if created:
        return

    # Get old and new status
    old_status = getattr(instance, "_old_status", None)
    new_status = instance.status

    # Skip if no status change
    if old_status == new_status:
        return

    # If status changed to 'confirmed', increase sold quantities AND generate tickets
    if old_status != "confirmed" and new_status == "confirmed":
        with transaction.atomic():
            # 1. Update inventory
            for item in instance.items.select_related(
                "ticket_type", "ticket_tier", "day_pass", "day_tier_price"
            ).all():
                # Update ticket type sold count using F() expression for atomic update
                from django.db.models import F
                from Tickets.models import TicketType, TicketTier, DayPass, DayTierPrice

                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_sold=F("quantity_sold") + item.quantity
                )

                # Update day_tier_price sold count if applicable (for tier_and_day pricing)
                if item.day_tier_price:
                    DayTierPrice.objects.filter(pk=item.day_tier_price.pk).update(
                        quantity_sold=F("quantity_sold") + item.quantity
                    )
                # Otherwise update individual tier and day_pass
                else:
                    # Update tier sold count if applicable
                    if item.ticket_tier:
                        TicketTier.objects.filter(pk=item.ticket_tier.pk).update(
                            quantity_sold=F("quantity_sold") + item.quantity
                        )

                    # Update day pass sold count if applicable
                    if item.day_pass:
                        DayPass.objects.filter(pk=item.day_pass.pk).update(
                            quantity_sold=F("quantity_sold") + item.quantity
                        )

            # 2. Generate individual tickets
            from Tickets.models import Ticket

            for item in instance.items.select_related(
                "ticket_type",
                "ticket_tier",
                "day_pass",
                "day_tier_price",
                "order__event",
            ).all():
                # Create individual ticket for each quantity
                for i in range(item.quantity):
                    Ticket.objects.create(
                        order_item=item,
                        event=item.order.event,
                        ticket_type=item.ticket_type,
                        ticket_tier=item.ticket_tier,
                        day_pass=item.day_pass,
                        day_tier_price=item.day_tier_price,
                        ticket_name=item.ticket_name,
                        tier_name=item.tier_name,
                        day_name=item.day_name,
                        event_date=item.order.event.start_date,
                        price=item.unit_price,
                        status="active",
                    )

            logger.info(
                f"Generated {instance.total_tickets} individual tickets for order {instance.order_number}"
            )

    # If status changed from 'confirmed' to 'cancelled'/'refunded', restore inventory AND cancel tickets
    elif old_status == "confirmed" and new_status in ["cancelled", "refunded"]:
        with transaction.atomic():
            from django.db.models import F
            from Tickets.models import (
                TicketType,
                TicketTier,
                DayPass,
                DayTierPrice,
                Ticket,
            )

            for item in instance.items.select_related(
                "ticket_type", "ticket_tier", "day_pass", "day_tier_price"
            ).all():
                # Restore ticket type quantity using F() expression
                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_sold=F("quantity_sold") - item.quantity
                )

                # Restore day_tier_price quantity if applicable
                if item.day_tier_price:
                    DayTierPrice.objects.filter(pk=item.day_tier_price.pk).update(
                        quantity_sold=F("quantity_sold") - item.quantity
                    )
                # Otherwise restore individual tier and day_pass
                else:
                    # Restore tier quantity if applicable
                    if item.ticket_tier:
                        TicketTier.objects.filter(pk=item.ticket_tier.pk).update(
                            quantity_sold=F("quantity_sold") - item.quantity
                        )

                    # Restore day pass quantity if applicable
                    if item.day_pass:
                        DayPass.objects.filter(pk=item.day_pass.pk).update(
                            quantity_sold=F("quantity_sold") - item.quantity
                        )

            # Cancel all tickets for this order
            cancelled_count = Ticket.objects.filter(
                order_item__order=instance, status="active"
            ).update(status="cancelled")

            logger.info(
                f"Cancelled {cancelled_count} tickets for order {instance.order_number}"
            )


@receiver(pre_delete, sender=Order)
def restore_inventory_on_order_delete(sender, instance, **kwargs):
    """
    Restore ticket inventory if a confirmed order is deleted
    """
    if instance.status == "confirmed":
        with transaction.atomic():
            from django.db.models import F
            from Tickets.models import TicketType, TicketTier, DayPass, DayTierPrice

            for item in instance.items.select_related(
                "ticket_type", "ticket_tier", "day_pass", "day_tier_price"
            ).all():
                # Restore ticket type quantity using F() expression
                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_sold=F("quantity_sold") - item.quantity
                )

                # Restore day_tier_price quantity if applicable
                if item.day_tier_price:
                    DayTierPrice.objects.filter(pk=item.day_tier_price.pk).update(
                        quantity_sold=F("quantity_sold") - item.quantity
                    )
                # Otherwise restore individual tier and day_pass
                else:
                    # Restore tier quantity if applicable
                    if item.ticket_tier:
                        TicketTier.objects.filter(pk=item.ticket_tier.pk).update(
                            quantity_sold=F("quantity_sold") - item.quantity
                        )

                    # Restore day pass quantity if applicable
                    if item.day_pass:
                        DayPass.objects.filter(pk=item.day_pass.pk).update(
                            quantity_sold=F("quantity_sold") - item.quantity
                        )
