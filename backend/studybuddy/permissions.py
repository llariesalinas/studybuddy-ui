from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to users with the 'Admin' or 'SuperAdmin' role (or Django staff/superusers).
    SuperAdmin is a superset of Admin and must pass all admin-gated views.
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        return bool(
            hasattr(user, 'userprofile') and
            user.userprofile.role in ('Admin', 'SuperAdmin')
        )

class IsSuperAdminUser(permissions.BasePermission):
    """
    Allows access only to users with the 'SuperAdmin' role or superusers.
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return bool(
            hasattr(user, 'userprofile') and
            user.userprofile.role == 'SuperAdmin'
        )
