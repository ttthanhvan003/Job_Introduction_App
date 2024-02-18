from rest_framework import permissions

class OwnerAuthenticated(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and request.user == obj.candidate

class IsUserOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view) and obj == request.user

class IsUserCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'candidate'

class IsUserEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'employer'

# class IsUserAdmin(permissions.IsAuthenticated):
#     def has_permission(self, request, view):
#         return request.user.is_staff