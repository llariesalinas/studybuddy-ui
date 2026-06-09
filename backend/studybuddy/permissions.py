from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to app admins or Django staff/superusers.
    """
    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if user.is_staff or user.is_superuser:
            return True

        return bool(
            hasattr(user, 'userprofile') and
            user.userprofile.role == 'Admin'
        )
