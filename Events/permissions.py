"""
Custom permissions for Events app
"""

from rest_framework import permissions


class IsOrganizer(permissions.BasePermission):
    """
    Permission to check if user is an organizer
    """

    message = "Only organizers can perform this action"

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == "organizer"
        )


class IsEventOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the event
    """

    message = "You can only modify your own events"

    def has_object_permission(self, request, view, obj):
        # Allow admin to access everything
        if request.user.is_staff or request.user.user_type == "admin":
            return True

        # Check if user is the organizer of this event
        return obj.organizer == request.user


class IsEventOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission to allow read-only access to everyone,
    but write access only to event owner
    """

    def has_permission(self, request, view):
        # Allow read permissions for any request
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

        # Write permissions only for event owner
        return obj.organizer == request.user
