"""
Custom permissions for Orders app
"""

from rest_framework import permissions


class IsOrderOwner(permissions.BasePermission):
    """
    Permission to only allow owners of an order to access it
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns the order"""
        return obj.user == request.user


class IsOrderOwnerOrAdmin(permissions.BasePermission):
    """
    Permission to allow order owners or admins to access orders
    """

    def has_object_permission(self, request, view, obj):
        """Check if user owns the order or is admin"""
        return obj.user == request.user or request.user.is_staff
