"""
Signals for Orders app
Handles ticket inventory updates when orders are confirmed/cancelled
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.db import transaction

from .models import Order, OrderItem


@receiver(post_save, sender=Order)
def update_ticket_inventory_on_order_save(sender, instance, created, **kwargs):
    """
    Update ticket inventory when order status changes
    - When order is confirmed: increase quantity_sold
    - When order is cancelled/failed: decrease quantity_sold (restore inventory)
    """
    if not created:  # Only for updates, not creation
        # Get the previous status from database
        try:
            old_instance = Order.objects.get(pk=instance.pk)
        except Order.DoesNotExist:
            return

        old_status = (
            Order.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )
        new_status = instance.status

        # If status changed to 'confirmed', increase sold quantities
        if old_status != "confirmed" and new_status == "confirmed":
            with transaction.atomic():
                for item in instance.items.all():
                    # Update ticket type sold count
                    ticket_type = item.ticket_type
                    ticket_type.quantity_sold += item.quantity
                    ticket_type.save()

                    # Update tier sold count if applicable
                    if item.ticket_tier:
                        tier = item.ticket_tier
                        tier.quantity_sold += item.quantity
                        tier.save()

                    # Update day pass sold count if applicable
                    if item.day_pass:
                        day_pass = item.day_pass
                        day_pass.quantity_sold += item.quantity
                        day_pass.save()

        # If status changed from 'confirmed' to 'cancelled'/'refunded', restore inventory
        elif old_status == "confirmed" and new_status in ["cancelled", "refunded"]:
            with transaction.atomic():
                for item in instance.items.all():
                    # Restore ticket type quantity
                    ticket_type = item.ticket_type
                    ticket_type.quantity_sold = max(
                        0, ticket_type.quantity_sold - item.quantity
                    )
                    ticket_type.save()

                    # Restore tier quantity if applicable
                    if item.ticket_tier:
                        tier = item.ticket_tier
                        tier.quantity_sold = max(0, tier.quantity_sold - item.quantity)
                        tier.save()

                    # Restore day pass quantity if applicable
                    if item.day_pass:
                        day_pass = item.day_pass
                        day_pass.quantity_sold = max(
                            0, day_pass.quantity_sold - item.quantity
                        )
                        day_pass.save()


@receiver(pre_delete, sender=Order)
def restore_inventory_on_order_delete(sender, instance, **kwargs):
    """
    Restore ticket inventory if a confirmed order is deleted
    """
    if instance.status == "confirmed":
        with transaction.atomic():
            for item in instance.items.all():
                # Restore ticket type quantity
                ticket_type = item.ticket_type
                ticket_type.quantity_sold = max(
                    0, ticket_type.quantity_sold - item.quantity
                )
                ticket_type.save()

                # Restore tier quantity if applicable
                if item.ticket_tier:
                    tier = item.ticket_tier
                    tier.quantity_sold = max(0, tier.quantity_sold - item.quantity)
                    tier.save()

                # Restore day pass quantity if applicable
                if item.day_pass:
                    day_pass = item.day_pass
                    day_pass.quantity_sold = max(
                        0, day_pass.quantity_sold - item.quantity
                    )
                    day_pass.save()
