"""
Signals for Orders app
Handles ticket inventory updates when orders are confirmed/cancelled
"""

from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.db import transaction

from .models import Order, OrderItem


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

    # If status changed to 'confirmed', increase sold quantities
    if old_status != "confirmed" and new_status == "confirmed":
        with transaction.atomic():
            for item in instance.items.select_related(
                "ticket_type", "ticket_tier", "day_pass"
            ).all():
                # Update ticket type sold count using F() expression for atomic update
                from django.db.models import F
                from Tickets.models import TicketType, TicketTier, DayPass

                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_sold=F("quantity_sold") + item.quantity
                )

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

    # If status changed from 'confirmed' to 'cancelled'/'refunded', restore inventory
    elif old_status == "confirmed" and new_status in ["cancelled", "refunded"]:
        with transaction.atomic():
            from django.db.models import F
            from Tickets.models import TicketType, TicketTier, DayPass

            for item in instance.items.select_related(
                "ticket_type", "ticket_tier", "day_pass"
            ).all():
                # Restore ticket type quantity using F() expression
                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_sold=F("quantity_sold") - item.quantity
                )

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


@receiver(pre_delete, sender=Order)
def restore_inventory_on_order_delete(sender, instance, **kwargs):
    """
    Restore ticket inventory if a confirmed order is deleted
    """
    if instance.status == "confirmed":
        with transaction.atomic():
            from django.db.models import F
            from Tickets.models import TicketType, TicketTier, DayPass

            for item in instance.items.select_related(
                "ticket_type", "ticket_tier", "day_pass"
            ).all():
                # Restore ticket type quantity using F() expression
                TicketType.objects.filter(pk=item.ticket_type.pk).update(
                    quantity_sold=F("quantity_sold") - item.quantity
                )

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
                if item.day_pass:
                    day_pass = item.day_pass
                    day_pass.quantity_sold = max(
                        0, day_pass.quantity_sold - item.quantity
                    )
                    day_pass.save(update_fields=["quantity_sold"])
