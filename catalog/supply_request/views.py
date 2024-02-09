from .serializers import SupplyRequestSerializer, SupplyRequestStatusSerializer, SupplyRequestPositionSerializer
from .models import SupplyRequest, SupplyRequestStatus, SupplyRequestPosition
from catalog.company.models import Company
from catalog.company.permissions import IsOwnerOrCompanyAdmin
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsCustomer, IsSupplierOrCustomer, IsOpen, IsSupplier, IsPositionSupplierOrCustomer, \
    IsSupplierStatusNew, IsCustomerStatus, SupplierCanUpdateStatus
from rest_framework import status
from rest_framework.response import Response
from django.db.models import Q


class SupplyRequestStatusListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SupplyRequestStatusSerializer

    def get_queryset(self):
        queryset = SupplyRequestStatus.objects.language().fallbacks('en').order_by('position')
        return queryset


class CreateSupplyRequestView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsCustomer)

    serializer_class = SupplyRequestSerializer
    queryset = SupplyRequest.objects.all()

    def get_serializer_context(self):

        try:
            company = self.request.data['customer_company']
        except:
            company = None

        return {'request': self.request, 'company': company}


class UpdateSupplyRequestView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,  IsSupplierOrCustomer)
    serializer_class = SupplyRequestSerializer
    queryset = SupplyRequest.objects.all()


class UpdateSupplyRequestPositionView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPositionSupplierOrCustomer)
    serializer_class = SupplyRequestPositionSerializer
    queryset = SupplyRequestPosition.objects.all()


class DeleteSupplyRequestView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsCustomer, IsOpen)
    serializer_class = SupplyRequestSerializer
    queryset = SupplyRequest.objects.all()


class DeleteSupplyRequestPositionView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsPositionSupplierOrCustomer)
    serializer_class = SupplyRequestPositionSerializer
    queryset = SupplyRequestPosition.objects.all()


class SupplyRequestView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSupplierOrCustomer)
    serializer_class = SupplyRequestSerializer
    queryset = SupplyRequest.objects.all()


class UserSupplyRequestsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SupplyRequestSerializer

    def get_serializer_context(self):

        return {'request': self.request, 'company': None}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        request_status = self.request.GET.get('status', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        keyword = self.request.GET.get('keyword', None)

        filter_list = Q(customer_user=self.request.user)

        if request_status is not None:
            filter_list = filter_list & Q(status=request_status)

        if keyword:
            filter_list = filter_list & Q(id=int(keyword))

        if country is not None:
            filter_list = filter_list & (
                    Q(supplier_user__user_profile__country=country) | Q(supplier_company__country=country))
        if city is not None:
            filter_list = filter_list & (
                    Q(supplier_user__user_profile__city=city) | Q(supplier_company__city=city))
        if region is not None:
            filter_list = filter_list & (
                    Q(supplier_user__user_profile__city__region=region) | Q(supplier_company__city__region=region))

        if page == 0:
            objects = SupplyRequest.objects.filter(filter_list).order_by(order)[:10]


        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = SupplyRequest.objects.filter(filter_list).order_by(order)[item_from:item_to]

        return objects


class UserSalesRequestsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SupplyRequestSerializer

    def get_serializer_context(self):

        return {'request': self.request, 'company': None}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        request_status = self.request.GET.get('status', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        keyword = self.request.GET.get('keyword', None)

        filter_list = Q(supplier_user=self.request.user, show_to_supplier=True)

        if request_status is not None:
            filter_list = filter_list & Q(status=request_status)

        if keyword:
            filter_list = filter_list & Q(id=int(keyword))

        if country is not None:
            filter_list = filter_list & (
                    Q(customer_user__user_profile__country=country) | Q(customer_company__country=country))
        if city is not None:
            filter_list = filter_list & (
                    Q(customer_user__user_profile__city=city) | Q(customer_company__city=city))
        if region is not None:
            filter_list = filter_list & (
                    Q(customer_user__user_profile__city__region=region) | Q(customer_company__city__region=region))

        if page == 0:
            objects = SupplyRequest.objects.filter(filter_list).exclude(status__code='new').order_by(order)[:10]


        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = SupplyRequest.objects.filter(filter_list).exclude(status__code='new').order_by(order)[
                      item_from:item_to]

        return objects


class CompanySupplyRequestsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = SupplyRequestSerializer

    def get_serializer_context(self):

        company = int(self.kwargs['company'])
        return {'request': self.request, 'company': company}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        company = int(self.kwargs['company'])
        order = self.kwargs['order']

        company_object = Company.objects.language().fallbacks('en').get(id=company)
        self.check_object_permissions(self.request, company_object)

        request_status = self.request.GET.get('status', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        keyword = self.request.GET.get('keyword', None)

        filter_list = Q(customer_company=company_object)

        if request_status is not None:
            filter_list = filter_list & Q(status=request_status)
        if keyword:
            filter_list = filter_list & Q(id=int(keyword))

        if country is not None:
            filter_list = filter_list & (
                    Q(supplier_user__user_profile__country=country) | Q(supplier_company__country=country))
        if city is not None:
            filter_list = filter_list & (
                    Q(supplier_user__user_profile__city=city) | Q(supplier_company__city=city))
        if region is not None:
            filter_list = filter_list & (
                    Q(supplier_user__user_profile__city__region=region) | Q(supplier_company__city__region=region))

        if page == 0:
            objects = SupplyRequest.objects.filter(filter_list).order_by(order)[:10]


        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = SupplyRequest.objects.filter(filter_list).order_by(order)[
                      item_from:item_to]

        return objects


class CompanySalesRequestsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = SupplyRequestSerializer

    def get_serializer_context(self):

        company = int(self.kwargs['company'])
        return {'request': self.request, 'company': company}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        company = int(self.kwargs['company'])
        order = self.kwargs['order']

        company_object = Company.objects.language().fallbacks('en').get(id=company)
        self.check_object_permissions(self.request, company_object)

        request_status = self.request.GET.get('status', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        keyword = self.request.GET.get('keyword', None)

        filter_list = Q(supplier_company=company_object, show_to_supplier=True)

        if request_status is not None:
            filter_list = filter_list & Q(status=request_status)

        if keyword:
            filter_list = filter_list & Q(id=int(keyword))

        if country is not None:
            filter_list = filter_list & (
                    Q(customer_user__user_profile__country=country) | Q(customer_company__country=country))
        if city is not None:
            filter_list = filter_list & (
                    Q(customer_user__user_profile__city=city) | Q(customer_company__city=city))
        if region is not None:
            filter_list = filter_list & (
                    Q(customer_user__user_profile__city__region=region) | Q(customer_company__city__region=region))

        if page == 0:
            objects = SupplyRequest.objects.filter(filter_list).exclude(status__code='new').order_by(order)[:10]


        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = SupplyRequest.objects.filter(filter_list).exclude(status__code='new').order_by(order)[
                      item_from:item_to]

        return objects


class UpdateRequestCommentView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsSupplierStatusNew)
    serializer_class = SupplyRequestSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        req = self.kwargs['req']

        try:
            obj = SupplyRequest.objects.get(id=req)
        except SupplyRequest.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.supplier_comment = value
        obj.reviewed = True
        obj.need_confirmation = True
        obj.save()

        return Response({'value': value})


class UpdateRequestChargesView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsSupplierStatusNew)
    serializer_class = SupplyRequestSerializer

    def put(self, request, *args, **kwargs):
        value = int(request.data['value'])
        comment = request.data['comment']
        req = self.kwargs['req']

        try:
            obj = SupplyRequest.objects.get(id=req)
        except SupplyRequest.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.charges_comment = comment
        obj.charges = value
        obj.reviewed = True
        obj.need_confirmation = True
        obj.save()

        return Response({'value': value, comment: 'comment'})


class UpdateRequestStatusView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, SupplierCanUpdateStatus)
    serializer_class = SupplyRequestSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        req = self.kwargs['req']

        try:
            obj = SupplyRequest.objects.get(id=req)
        except SupplyRequest.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        new_status = SupplyRequestStatus.objects.get(code=value)
        obj.status = new_status
        obj.reviewed = True
        obj.save()

        return Response(SupplyRequestSerializer(obj, context={'request': request,
                                                              'company': obj.supplier_company_id}).data)


class UpdateRequestStatusByCustomerView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsCustomerStatus)
    serializer_class = SupplyRequestSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        req = self.kwargs['req']

        try:
            obj = SupplyRequest.objects.get(id=req)
        except SupplyRequest.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        new_status = SupplyRequestStatus.objects.get(code=value)
        if new_status.code == 'posted':
            obj.show_to_supplier = True
        obj.status = new_status
        obj.reviewed = True
        obj.save()

        return Response(SupplyRequestSerializer(obj, context={'request': request,
                                                              'company': obj.customer_company_id}).data)


class NewSupplyRequestView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsCustomer)
    serializer_class = SupplyRequestSerializer

    def get_serializer_context(self):
        try:
            company = self.request.data['customer_company']
        except:
            company = None

        return {'request': self.request, 'company': company}

    def post(self, request, *args, **kwargs):
        customer_company = self.request.data.get('customer_company', None)
        customer_user = self.request.data.get('customer_user', None)
        supplier_user = self.request.data.get('supplier_user', None)
        supplier_company = self.request.data.get('supplier_company', None)
        currency = self.request.data.get('currency', None)

        obj = SupplyRequest.objects.filter(customer_company=customer_company, customer_user=customer_user,
                                           supplier_user=supplier_user, supplier_company=supplier_company,
                                           status__code='new', currency=currency).first()
        if obj:

            self.check_object_permissions(self.request, obj)

            positions = self.request.data.pop('positions', None)
            if positions:
                for position in positions:
                    product = position.get('product')
                    price = position.get('price')

                    try:
                        pos_obj = SupplyRequestPosition.objects.get(supply_request=obj, product_id=product)
                        pos_obj.quantity = pos_obj.quantity + 1
                        pos_obj.save()
                    except SupplyRequestPosition.DoesNotExist:
                        SupplyRequestPosition.objects.create(supply_request=obj, product_id=product, quantity=1,
                                                             price=price)
                obj = SupplyRequest.objects.get(id=obj.id)
        else:
            self.check_object_permissions(self.request,
                                          SupplyRequest(customer_company_id=customer_company,
                                                        customer_user_id=customer_user))
            serializer = SupplyRequestSerializer(data=request.data)

            if serializer.is_valid():
                obj = serializer.save()


            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(SupplyRequestSerializer(obj, context={'request': request,
                                                              'company': obj.customer_company_id}).data)
