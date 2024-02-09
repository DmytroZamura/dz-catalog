from rest_framework import permissions
from catalog.company.models import CompanyUser
from catalog.community.models import CommunityMember

class IsOwnerOrCompanyAdmin(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user

        if obj.company != None:
            res = CompanyUser.objects.filter(company=obj.company, user=request.user).exists()



        return res


class IsOwner(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user



        return res

class IsPostOwnerOrCompanyAdmin(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.post.user == request.user

        if obj.post.company:
            res = CompanyUser.objects.filter(company=obj.post.company, user=request.user).exists()



        return res


class IsPostOwnerOrCompanyAdminStrict(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.

        res = obj.post.user == request.user

        if obj.post.company:
            res = CompanyUser.objects.filter(company=obj.post.company, user=request.user).exists()



        return res

class CanDeletePost(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user

        if obj.company:
            res = CompanyUser.objects.filter(company=obj.company, user=request.user).exists()

        if not res and obj.community:
            res = CommunityMember.objects.filter(community=obj.community, user=request.user, admin=True).exists()

        return res


class CanDeletePostObject(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user
        if not res:
            res = obj.post.user == request.user

        if not res and obj.post.community:
            res = CommunityMember.objects.filter(community=obj.post.community, user=request.user, admin=True).exists()

        return res