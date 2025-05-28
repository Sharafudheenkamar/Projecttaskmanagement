from rest_framework import permissions
from .models import UserProfile, Role

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'userprofile') and \
               request.user.userprofile.role.name == 'SuperAdmin'

class IsAdminOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile'):
            return False
        role = request.user.userprofile.role.name
        return role in ['Admin', 'SuperAdmin']

class IsTaskAssigneeOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated or not hasattr(request.user, 'userprofile'):
            return False
        role = request.user.userprofile.role.name
        if role == 'SuperAdmin':
            return True
        if role == 'Admin':
            return obj.assigned_to.userprofile.assigned_admin == request.user
        return obj.assigned_to == request.user
