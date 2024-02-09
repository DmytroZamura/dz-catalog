from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from rest_framework import serializers
from .models import PaymentProduct, PaymentOrder, Payment, PaymentAccount
from catalog.general.serializers import UnitTypeSerializer, CurrencySerializer
from catalog.user_profile.serializers import UserWithProfileSmallSerializer
from catalog.company.serializers import CompanySmallSerializer
from catalog.post.serializers import PostShortSerializer
from catalog.product.serializers import ProductShortSerializer


class PaymentProductSerializer(TranslatableModelSerializer):
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)

    class Meta:
        model = PaymentProduct
        fields = ('id', 'name', 'description', 'code', 'unit_type', 'unit_type_details')


class PaymentProductSmallSerializer(TranslatableModelSerializer):
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)

    class Meta:
        model = PaymentProduct
        fields = ('id', 'name', 'code', 'unit_type', 'unit_type_details')


class PaymentAccountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=False)
    currency_details = CurrencySerializer(source='currency', required=False, read_only=True)
    company_details = CompanySmallSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanySmallSerializer(source='company', required=False, read_only=True, language='en')
    user_details = UserWithProfileSmallSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = PaymentAccount
        fields = (
        'id', 'user', 'user_details', 'company', 'company_details', 'company_default_details', 'balance', 'currency',
        'currency_details', 'update_date', 'create_date')


class PaymentOrderSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=False)
    payment_product_details = PaymentProductSmallSerializer(source='payment_product', required=False, read_only=True)

    class Meta:
        model = PaymentOrder
        fields = ('id', 'account', 'payment_product', 'payment_product_details', 'quantity',
                  'promoted_post', 'promoted_company', 'promoted_product',
                  'price', 'sum', 'create_date')

class PaymentOrderItemSerializer(PaymentOrderSerializer):
    promoted_post_details = PostShortSerializer(source='promoted_post', required=False, read_only=True)
    promoted_product_details = ProductShortSerializer(source='promoted_product', required=False, read_only=True)
    promoted_company_details = CompanySmallSerializer(source='promoted_company', required=False, read_only=True)

    class Meta(PaymentOrderSerializer.Meta):
        fields = PaymentOrderSerializer.Meta.fields + ( 'promoted_post_details',
                                                       'promoted_company_details',
                                                       'promoted_product_details')


class PaymentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = Payment
        fields = ('id', 'account', 'sum', 'callback_link', 'create_date')
