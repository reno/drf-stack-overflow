from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow the user to modify its data.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS or
            obj.user.id == request.user.id
        )


class IsOriginalPoster(permissions.BasePermission):
    """
    Object-level permission to only allow OP to accept answer.
    """

    def has_object_permission(self, request, view, obj):
        return obj.question.user.id == request.user.id



