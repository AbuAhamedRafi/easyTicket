"""
Custom permissions for Tickets app
"""

from rest_framework import permissions


class IsEventOrganizer(permissions.BasePermission):
    """
    Permission to check if user is the organizer of the event
    associated with the ticket
    """

    message = "Only the event organizer can manage tickets"

    def has_object_permission(self, request, view, obj):
        # Allow admin access
        if request.user.is_staff or request.user.user_type == "admin":
            return True

        # Check if user is the organizer of the event
        # obj could be TicketType, TicketTier, or DayPass
        if hasattr(obj, "event"):
            return obj.event.organizer == request.user
        elif hasattr(obj, "ticket_type"):
            return obj.ticket_type.event.organizer == request.user

        return False


class IsEventOrganizerOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access to everyone,
    but write access only to event organizer
    """

    def has_permission(self, request, view):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Read permissions for anyone
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admin can modify anything
        if request.user.is_staff or request.user.user_type == "admin":
            return True

        # Write permissions only for event organizer
        if hasattr(obj, "event"):
            return obj.event.organizer == request.user
        elif hasattr(obj, "ticket_type"):
            return obj.ticket_type.event.organizer == request.user

        return False
