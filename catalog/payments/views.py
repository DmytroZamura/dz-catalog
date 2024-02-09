from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import PaymentAccountSerializer, PaymentSerializer, PaymentProductSerializer, \
    PaymentOrderSerializer, PaymentOrderItemSerializer
from django.db.models import Q
from .models import PaymentOrder, ProductPrice, PaymentProduct, Payment, PaymentAccount, check_payment_account, \
    post_product_codes
from catalog.category.models import Category
from catalog.company.permissions import IsUserOrCompanyAdmin
from catalog.company.models import CompanyUser
from catalog.post.models import Post
from catalog.general.models import Translation
from catalog.post.serializers import PostShortSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from cloudipsp import Api, Checkout
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.utils import translation


# Create your views here.
class PaymentOrdersByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)
    serializer_class = PaymentOrderItemSerializer

    def get_queryset(self):

        page = int(self.kwargs['page'])
        account = self.request.GET.get('account', None)

        filter_list = Q(account=account)

        account = PaymentAccount.objects.get(id=account)

        self.check_object_permissions(self.request, account)

        orders = PaymentOrder.objects.filter(filter_list).order_by('-id')

        if page == 0:
            orders = orders[:20]
        else:
            item_from = page * 20
            item_to = page * 20 + 20
            orders = orders[item_from:item_to]

        return orders


class PaymentsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)
    serializer_class = PaymentSerializer

    def get_queryset(self):

        page = int(self.kwargs['page'])
        account = self.request.GET.get('account', None)

        filter_list = Q(account=account, confirmed=True)

        account = PaymentAccount.objects.get(id=account)

        self.check_object_permissions(self.request, account)

        payments = Payment.objects.filter(filter_list).order_by('-id')

        if page == 0:
            payments = payments[:20]
        else:
            item_from = page * 20
            item_to = page * 20 + 20
            payments = payments[item_from:item_to]

        return payments


def get_product_price(product, category, country):
    # print('product - '+str(product), ', category - ' + str(category) + ', country - ' + str(country) )
    filter_list = Q(product=product)

    if category is not None:
        filter_list = filter_list & Q(category=category)
    else:
        filter_list = filter_list & Q(category__isnull=True)
    if country is not None:
        filter_list = filter_list & Q(country=country)
    else:
        filter_list = filter_list & Q(country__isnull=True)

    try:
        price = ProductPrice.objects.get(filter_list)
        return price
    except ProductPrice.DoesNotExist:
        try:
            if category:
                category_obj = Category.objects.get(id=category)
                if category_obj.parent:
                    price = get_product_price(product, category_obj.parent.id, country)
                    return price
                else:
                    price = get_product_price(product, None, country)
                    return price
            else:
                return None

        except Category.DoesNotExist:
            return None


class ProductPriceView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, code):
        price = {
            'price_uah': settings.DEFAULT_PRICE_UAH,
            'price_usd': settings.DEFAULT_PRICE_USD,
            'product': None
        }

        try:
            product = PaymentProduct.objects.get(code=code)
            price['product'] = PaymentProductSerializer(product, context={'request': request}).data
        except PaymentProduct.DoesNotExist:
            return Response(price)
        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)

        price_obj = get_product_price(product.id, category, country)

        if price_obj:
            price['price_uah'] = price_obj.price_uah
            price['price_usd'] = price_obj.price_usd
            return Response(price)
        else:
            return Response(price)


class ProductPriceForObjectView(APIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)

    def get(self, request, code, id):
        price = {
            'price': 1,
            'product': None,
            'object': None,
            'account': None
        }

        price_uah = settings.DEFAULT_PRICE_UAH
        price_usd = settings.DEFAULT_PRICE_USD
        category = None
        country = None
        company = None

        if code in post_product_codes:
            try:
                obj = Post.objects.get(id=id)
                price['object'] = PostShortSerializer(obj, context={'request': request}).data
                if obj.category:
                    category = obj.category.id
                if obj.country:
                    country = obj.country.id
                company = obj.company
            except Post.DoesNotExist:
                return status.HTTP_400_BAD_REQUEST

        if company:
            try:
                account = PaymentAccount.objects.get(company=company)
            except PaymentAccount.DoesNotExist:
                return status.HTTP_400_BAD_REQUEST
        else:
            try:
                account = PaymentAccount.objects.get(user=self.request.user)
            except PaymentAccount.DoesNotExist:
                return status.HTTP_400_BAD_REQUEST

        self.check_object_permissions(self.request, account)
        price['account'] = PaymentAccountSerializer(account, context={'request': request}).data

        try:
            product = PaymentProduct.objects.get(code=code)
            price['product'] = PaymentProductSerializer(product, context={'request': request}).data
        except PaymentProduct.DoesNotExist:
            return status.HTTP_400_BAD_REQUEST

        price_obj = get_product_price(product.id, category, country)

        if price_obj:
            price_uah = price_obj.price_uah
            price_usd = price_obj.price_usd

        if account.currency.code == 'UAH':
            price['price'] = price_uah
        else:
            price['price'] = price_usd

        return Response(price)


class CheckPaymentAccounts(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):

        user = self.request.user

        if user.user_profile.country:
            if user.user_profile.country.code == 'UKR':
                check_payment_account(user, None, 'UAH')
            else:
                check_payment_account(user, None, 'USD')

        companies = user.managed_companies

        for company in companies.all():
            if company.company.country:
                if company.company.country.code == 'UKR':
                    check_payment_account(None, company.company, 'UAH')
                else:
                    check_payment_account(None, company.company, 'USD')

        return Response({'result': 1})


class PaymentAccountView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)
    serializer_class = PaymentAccountSerializer

    def get_object(self):
        id = int(self.kwargs['id'])
        account = PaymentAccount.objects.get(pk=id)

        self.check_object_permissions(self.request, account)

        return account


class PaymentAccountsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentAccountSerializer

    def get_queryset(self):
        user = self.request.user

        managed_companies = CompanyUser.objects.filter(user=user)
        companies = []
        for item in managed_companies.all():
            companies.append(item.company)

        filter_list = Q(user=user) | Q(company__in=companies)

        accounts = PaymentAccount.objects.filter(filter_list)

        return accounts


class CreatePaymentView(APIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)

    def post(self, request):
        account = request.data.get('account', None)

        account_obj = PaymentAccount.objects.get(id=account)
        self.check_object_permissions(self.request, account_obj)
        callback_link = request.data.get('callback_link', None)
        sum = request.data.get('sum', None)
        api = Api(merchant_id=settings.FONDY_MERCHANT_ID,
                  secret_key=settings.FONDY_SECRET_KEY)
        checkout = Checkout(api=api)

        payment = Payment.objects.create(account=account_obj, sum=sum, confirmed=False, callback_link=callback_link)
        order_id = payment.order_id
        product_trans = Translation.objects.language().fallbacks('en').get(code='payment-product-description')
        lang = translation.get_language()
        data = {
            "currency": account_obj.currency.code,
            "amount": sum * 100,
            "response_url": settings.PAYMENT_CALLBACK_URL,
            "order_desc": product_trans.text,
            "product_id": account,
            "order_id": str(order_id),
            "lang": lang

        }
        url = checkout.url(data).get('checkout_url')
        return Response(url)
        # account = request.data.get('account', None)
        #
        # account_obj = PaymentAccount.objects.get(id=account)
        # self.check_object_permissions(self.request, account_obj)
        # serializer = PaymentSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateOrderView(APIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)

    def post(self, request):
        account = request.data.get('account', None)

        account_obj = PaymentAccount.objects.get(id=account)
        self.check_object_permissions(self.request, account_obj)
        serializer = PaymentOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentCallbackView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # print(request.data)
        order_id = request.data.get('order_id', None)
        account = request.data.get('product_id', None)
        payment_id = request.data.get('payment_id', None)
        amount = request.data.get('amount', None)
        response_status = request.data.get('response_status', None)

        payment = Payment.objects.get(account_id=account, order_id=order_id, confirmed=False, sum=Decimal(amount) / 100)
        link = settings.FRONTEND_URL + payment.callback_link + '&response_status=' + response_status
        if response_status == 'success':
            payment.confirmed = True
            payment.payment_id = payment_id
            payment.save()

        return HttpResponseRedirect(link)
