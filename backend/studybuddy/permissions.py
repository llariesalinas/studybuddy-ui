from rest_framework import permissions

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
