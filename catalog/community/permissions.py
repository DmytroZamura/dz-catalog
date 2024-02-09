from rest_framework import permissions
from catalog.community.models import CommunityMember
from catalog.company.models import CompanyUser


# from catalog.community.models import CommunityMember

class IsOwnerOrCommunityAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        res = CommunityMember.objects.filter(community=obj.id, user=request.user, admin=True).exists()

        return res


class IsOwnerOrCommunityAdminDetails(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        res = CommunityMember.objects.filter(community=obj.community, user=request.user, admin=True).exists()

        return res


class IsOpenCommunityOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.community.open:
            res = True
        else:
            res = CommunityMember.objects.filter(community=obj.community, user=request.user, admin=True).exists()

        return res


class IsCompanyAdminOrCommunityAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        res1 = CommunityMember.objects.filter(community=obj.community, user=request.user, admin=True).exists()
        res2 = CompanyUser.objects.filter(company=obj.company, user=request.user).exists()

        res = res1 or res2

        return res


class IsUserOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.user == request.user:
            res = True
        else:
            res = CommunityMember.objects.filter(community=obj.community, user=request.user, admin=True).exists()

        return res


class IsCommunityMember(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        res = CommunityMember.objects.filter(community=obj.id, user=request.user).exists()

        return res


class IsCommunityMemberDetails(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        res = CommunityMember.objects.filter(community=obj.community, user=request.user).exists()

        return res


class IsInvitationUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        res = obj.user == request.user

        return res
