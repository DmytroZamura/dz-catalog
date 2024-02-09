from rest_framework import permissions
from catalog.company.models import CompanyUser


class IsOwnerOrCompanyAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        res = CompanyUser.objects.filter(company=obj.id, user=request.user).exists()

        return res


class IsOwnerOrCompanyAdminDetails(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        res = CompanyUser.objects.filter(company=obj.company, user=request.user).exists()

        return res


class IsUserOrCompanyAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.user == request.user:
            res = True
        else:
            res = CompanyUser.objects.filter(company=obj.company, user=request.user).exists()

        return res


class IsSupplier(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.supplier_user == request.user:
            res = True
        else:
            res = CompanyUser.objects.filter(company=obj.supplier_company, user=request.user).exists()

        return res


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user

        return res
