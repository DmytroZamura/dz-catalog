from rest_framework import permissions


class IsFollower(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user

        return res