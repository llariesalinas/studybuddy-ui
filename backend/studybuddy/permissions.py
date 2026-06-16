from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to users with the 'Admin' or 'SuperAdmin' role (or Django superusers).
    SuperAdmin is a superset of Admin and must pass all admin-gated views.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'userprofile') and
            (request.user.userprofile.role in ('Admin', 'SuperAdmin') or request.user.is_superuser)
        )

class IsSuperAdminUser(permissions.BasePermission):
    """
    Allows access only to users with the 'SuperAdmin' role or superusers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'userprofile') and 
            (request.user.userprofile.role == 'SuperAdmin' or request.user.is_superuser)
        )
