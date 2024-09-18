from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Only allow access if the user is a superuser
        return request.user and request.user.is_superuser
