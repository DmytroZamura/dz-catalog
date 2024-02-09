from .models import SupplyRequest, SupplyRequestPosition, SupplyRequestNote, SupplyRequestDocument, SupplyRequestChat, \
    SupplyRequestStatus
from rest_framework import serializers
from catalog.user_profile.serializers import UserWithProfileSerializer, UserWithProfileSmallSerializer
from catalog.general.serializers import CurrencySerializer
from catalog.company.serializers import CompanyShortSerializer, CompanySmallSerializer
from catalog.file.serializers import FileSerializer
from catalog.product.serializers import ProductShortSerializer
from catalog.messaging.serializers import ChatSerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer


class SupplyRequestStatusSerializer(TranslatableModelSerializer):
    class Meta:
        model = SupplyRequestStatus
        fields = ('id', 'code', 'name', 'icon', 'color_class')


class SupplyRequestNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyRequestNote
        fields = ('id', 'supply_request', 'user', 'reason_win_lost', 'update_date')

        read_only_fields = ('update_date',)


class SupplyRequestDocumentSerializer(serializers.ModelSerializer):
    file_details = FileSerializer(source='file', required=False, read_only=True)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = SupplyRequestDocument
        fields = ('id', 'file', 'file_details')

        read_only_fields = ('update_date',)


class SupplyRequestPositionSerializer(serializers.ModelSerializer):
    product_details = ProductShortSerializer(source='product', required=False, read_only=True)
    product_default_details = ProductShortSerializer(source='product', required=False, read_only=True, language='en')

    class Meta:
        model = SupplyRequestPosition
        fields = ('id', 'product', 'product_details', 'price', 'quantity', 'comment', 'update_date', 'total',
                  'product_default_details')

        read_only_fields = ('update_date', 'total',)


class SupplyRequestChatSerializer(serializers.ModelSerializer):
    chat_details = ChatSerializer(source='chat', required=False, read_only=True)

    class Meta:
        model = SupplyRequestChat
        fields = ('chat', 'supply_request', 'chat_details')


class SupplyRequestSerializer(serializers.ModelSerializer):
    customer_user_details = UserWithProfileSerializer(source='customer_user', required=False, read_only=True)
    customer_company_details = CompanyShortSerializer(source='customer_company', required=False, read_only=True)
    customer_company_default_details = CompanyShortSerializer(source='customer_company', required=False, read_only=True,
                                                              language='en')
    supplier_user_details = UserWithProfileSerializer(source='supplier_user', required=False, read_only=True)
    supplier_company_details = CompanyShortSerializer(source='supplier_company', required=False, read_only=True)
    supplier_company_default_details = CompanyShortSerializer(source='supplier_company', required=False, read_only=True,
                                                              language='en')
    positions = SupplyRequestPositionSerializer(many=True, required=False)
    documents = SupplyRequestDocumentSerializer(many=True, required=False)
    currency_details = CurrencySerializer(source='currency', required=False, read_only=True)
    status_details = SupplyRequestStatusSerializer(source='status', required=False, read_only=True)
    chat_details = SupplyRequestChatSerializer(source='chat', required=False, read_only=True)

    class Meta:
        model = SupplyRequest
        fields = ('id', 'supplier_request_id', 'status', 'status_details', 'need_confirmation', 'customer_user',
                  'customer_user_details',
                  'customer_company', 'customer_company_details', 'customer_company_default_details', 'contact_email',
                  'contact_phone', 'skype',
                  'customer_comment', 'supplier_user', 'supplier_user_details', 'supplier_company',
                  'supplier_company_details', 'supplier_company_default_details', 'supplier_comment', 'chat_details',
                  'currency', 'currency_details', 'positions', 'documents', 'charges', 'charges_comment',
                  'total_amount', 'delivery_address', 'update_date', 'create_date', 'canceled_by')

        read_only_fields = ('update_date',)

    def create(self, validated_data):

        positions = validated_data.pop('positions', None)
        documents = validated_data.pop('documents', None)
        request = SupplyRequest.objects.create(**validated_data)

        if positions:
            for position in positions:
                SupplyRequestPosition.objects.create(supply_request=request, **position)
        if documents:
            for document in documents:
                SupplyRequestDocument.objects.create(supply_request=request, **document)

        return request

    def update(self, instance: SupplyRequest, validated_data):

        documents = validated_data.pop('documents', None)
        positions = validated_data.pop('post_request_positions', None)

        # Request instance updating
        instance.customer_comment = validated_data['customer_comment']
        instance.contact_email = validated_data['contact_email']
        instance.contact_phone = validated_data['contact_phone']
        instance.skype = validated_data['skype']
        instance.delivery_address = validated_data['delivery_address']
        instance.currency = validated_data['currency']

        instance.save()

        # Documents add or delete
        documents_ids = []
        for item in documents:
            item_id = item.get('id', None)
            print(item_id)

            if item_id is not None:
                documents_ids.append(item_id)
            else:
                document = SupplyRequestDocument(supply_request=instance, file=item['file'])
                document.save()
                documents_ids.append(document.id)

        for document in instance.documents.all():
            if document.id not in documents_ids:
                document.delete()

        return instance


class SupplyRequestSmallSerializer(serializers.ModelSerializer):
    # customer_user_details = UserWithProfileSmallSerializer(source='customer_user', required=False, read_only=True)
    # customer_company_details = CompanySmallSerializer(source='customer_company', required=False, read_only=True)
    # customer_company_default_details = CompanySmallSerializer(source='customer_company', required=False, read_only=True,
    #                                                           language='en')
    # supplier_user_details = UserWithProfileSmallSerializer(source='supplier_user', required=False, read_only=True)
    # supplier_company_details = CompanySmallSerializer(source='supplier_company', required=False, read_only=True)
    # supplier_company_default_details = CompanySmallSerializer(source='supplier_company', required=False, read_only=True,
    #                                                           language='en')
    status_details = SupplyRequestStatusSerializer(source='status', required=False, read_only=True)


    class Meta:
        model = SupplyRequest
        fields = ('id', 'supplier_request_id', 'status', 'status_details', 'need_confirmation', 'customer_user',

                  'customer_company', 'contact_email',
                  'contact_phone', 'skype',
                  'customer_comment', 'supplier_user',  'supplier_company',
                  'supplier_comment',
                  'currency',
                  'total_amount',  'update_date', 'create_date', 'canceled_by')

        read_only_fields = ('update_date',)
