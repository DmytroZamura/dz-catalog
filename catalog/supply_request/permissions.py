from rest_framework import permissions
from catalog.company.models import CompanyUser


class IsCustomer(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        res = obj.customer_user == request.user
        if not res:
            res = CompanyUser.objects.filter(company=obj.customer_company, user=request.user).exists()

        return res


class IsCustomerStatus(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        res = False

        if obj.status.code == 'new' or obj.status.code == 'posted' or obj.status.code == 'confirm':
            res = True

        if res:

            res = obj.customer_user == request.user
            if not res:
                res = CompanyUser.objects.filter(company=obj.customer_company, user=request.user).exists()

        return res


class IsSupplier(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        res = obj.supplier_user == request.user

        if not res:
            res = CompanyUser.objects.filter(company=obj.supplier_company, user=request.user).exists()

        return res


class SupplierCanUpdateStatus(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        res = False

        if obj.status.code != 'c_canceled' and obj.status.code != 'new' and obj.status.code != 'confirm':
            res = True

        if res:
            res = obj.supplier_user == request.user

            if not res:
                res = CompanyUser.objects.filter(company=obj.supplier_company, user=request.user).exists()

        return res


class IsSupplierStatusNew(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        res = False

        if obj.status.code == 'posted':
            res = True

        if res:
            res = obj.supplier_user == request.user

            if not res:
                res = CompanyUser.objects.filter(company=obj.supplier_company, user=request.user).exists()

        return res


class IsSupplierOrCustomer(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        res = obj.supplier_user == request.user or obj.customer_user == request.user

        if not res:
            res = CompanyUser.objects.filter(company=obj.supplier_company, user=request.user).exists()
        if not res:
            res = CompanyUser.objects.filter(company=obj.customer_company, user=request.user).exists()

        return res


class IsPositionSupplierOrCustomer(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        res = obj.supply_request.supplier_user == request.user or obj.supply_request.customer_user == request.user

        if not res:
            res = CompanyUser.objects.filter(company=obj.supply_request.supplier_company, user=request.user).exists()
        if not res:
            res = CompanyUser.objects.filter(company=obj.supply_request.customer_company, user=request.user).exists()

        return res


class IsOpen(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        res = obj.status.code == 'new'
        return res
