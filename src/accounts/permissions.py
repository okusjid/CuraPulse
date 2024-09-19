from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow superusers to access the view.
    """
    def has_permission(self, request, view):
        # Only allow access if the user is a superuser
        return request.user and request.user.is_superuser


class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors to access their own appointments.
    """
    def has_permission(self, request, view):
        # Allow access if the user is authenticated and is a doctor
        return request.user and request.user.is_authenticated and getattr(request.user, 'is_doctor', False)

    def has_object_permission(self, request, view, obj):
        # Allow access only if the appointment belongs to the doctor
        return request.user.is_superuser or (request.user.is_doctor and obj.doctor == request.user)
