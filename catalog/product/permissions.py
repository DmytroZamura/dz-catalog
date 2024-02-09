from rest_framework import permissions
from catalog.company.models import CompanyUser

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

class IsOwnerOrCompanyAdminDetails(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.product.user == request.user

        if obj.product.company != None:
            res = CompanyUser.objects.filter(company=obj.product.company, user=request.user).exists()



        return res

class IsOwner(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        res = obj.user == request.user



        return res