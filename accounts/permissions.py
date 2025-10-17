from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class to allow only Admin users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(permissions.BasePermission):
    """
    Permission class to allow only Teacher users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'teacher'


class IsPupil(permissions.BasePermission):
    """
    Permission class to allow only Pupil users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'pupil'


class IsAdminOrTeacher(permissions.BasePermission):
    """
    Permission class to allow Admin or Teacher users
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['admin', 'teacher']


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission class to allow owners to access their own data or admins to access all
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj.user == request.user
