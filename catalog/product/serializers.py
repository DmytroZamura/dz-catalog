from rest_framework import serializers
from .models import Product, ProductImage, ProductGroup, ProductAttributeValue, ProductAttribute, FavoriteProduct, \
    ProductEventsQty
from catalog.company.models import CompanyUser
from catalog.user_profile.serializers import UserWithProfileSerializer, UserWithProfileSmallSerializer, \
    UserWithProfileMiddleSerializer
from catalog.category.serializers import CategorySerializer, SuggestedCategorySerializer
from catalog.general.serializers import CountrySerializer, UnitTypeSerializer, CurrencySerializer
from catalog.file.serializers import UserImageProductSerializer
from catalog.company.serializers import CompanyShortSerializer, CompanySmallSerializer, CompanyMiddleSerializer
from catalog.general.models import convert_price
from catalog.attribute.serializers import AttributeValueSerializer, AttributeSerializer
from catalog.category.models import CategoryAttribute
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from decimal import Decimal


class ProductEventsQtySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductEventsQty
        fields = (
            'publications', 'reviews', 'rating', 'videos', 'questions', 'related_questions', 'related_reviews')


class ProductGroupSerializer(TranslatableModelSerializer):
    class Meta:
        model = ProductGroup
        fields = ('id', 'name', 'company', 'user', 'parent',  'child_qty', 'language_code')


class ProductImageSerializer(serializers.ModelSerializer):
    image_details = UserImageProductSerializer(source='image', required=False, read_only=True)

    class Meta:
        model = ProductImage
        fields = (
            'id', 'product', 'image', 'image_details', 'title', 'description', 'position')


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    value_list_details = AttributeValueSerializer(source='value_list', required=False, read_only=True)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = ProductAttributeValue
        fields = (
            'id', 'value_string', 'value_number', 'value_integer', 'value_boolean', 'value_list', 'value_list_details')


class ProductAttributeSerializer(serializers.ModelSerializer):
    attribute_details = AttributeSerializer(source='attribute', required=False, read_only=True)
    values = ProductAttributeValueSerializer(many=True, required=False)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = ProductAttribute
        fields = ('id', 'attribute', 'attribute_details', 'name', 'user_attribute', 'multiple', 'values')


def get_price_in_current_currency(context, obj_price, obj_currency):
    if context and obj_price and obj_currency:
        current_currency = context.get('current_currency', None)
        rate_usd = context.get('rate_usd', None)

        if current_currency:
            current_currency = int(current_currency)
            if rate_usd:
                rate_usd = Decimal(rate_usd)

            price = convert_price(obj_price, obj_currency.id, current_currency, rate_usd)
        else:
            price = obj_price
        return price
    else:
        return None


class ProductSerializer(TaggitSerializer, TranslatableModelSerializer):
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)
    origin_details = CountrySerializer(source='origin', required=False, read_only=True)
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)
    currency_details = CurrencySerializer(source='currency', required=False, read_only=True)
    company_details = CompanyShortSerializer(source="company", required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source="company", required=False, read_only=True, language='en')
    suggested_category_details = SuggestedCategorySerializer(source="suggested_category", required=False,
                                                             read_only=True)

    product_group_details = ProductGroupSerializer(source="product_group", required=False, read_only=True)
    product_group_details_default = ProductGroupSerializer(source="product_group", required=False, read_only=True,
                                                           language='en')
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, required=False)
    eventsqty = ProductEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    price_from_current_currency = serializers.SerializerMethodField()
    price_to_current_currency = serializers.SerializerMethodField()
    discount_price_from_current_currency = serializers.SerializerMethodField()
    discount_price_to_current_currency = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    favorite_status = serializers.SerializerMethodField()
    admin_status = serializers.SerializerMethodField()

    def get_admin_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                if obj.user_id == self.context['request'].user.id:
                    status = True
                else:
                    if obj.company:
                        status = CompanyUser.objects.filter(user=self.context['request'].user, company=obj.company,
                                                            admin=True).exists()
        return status

    def get_favorite_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = FavoriteProduct.objects.filter(user=self.context['request'].user, product=obj).exists()
        return status

    def get_price_from_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.price_from, obj.currency)

    def get_price_to_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.price_to, obj.currency)

    def get_discount_price_from_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.discount_price_from, obj.currency)

    def get_discount_price_to_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.discount_price_to, obj.currency)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'images', 'company', 'company_details', 'suggested_category', 'suggested_category_details',
            'product_group', 'product_group_details', 'seo_title', 'seo_description',
            'product_group_details_default', 'category', 'category_details', 'short_description',
            'model_number', 'brand_name', 'origin', 'tags', 'published', 'admin_status',
            'origin_details', 'attributes', 'link_to_buy', 'packaging_and_delivery', 'company_default_details',
            'product_or_service', 'unit_type', 'unit_type_details', 'slug', 'user_data', 'user',
            'published', 'price_from', 'price_to', 'price_from_current_currency', 'price_to_current_currency',
            'discount', 'deadline', 'weight_kg',
            'discount_price_from', 'discount_price_to',
            'discount_price_from_current_currency', 'discount_price_to_current_currency',
            'one_price', 'currency', 'currency_details', 'price_conditions',
            'eventsqty',
            'create_date', 'favorite_status', 'language_code', 'deleted')
        read_only_fields = ('create_date',)

    def create(self, validated_data):

        validated_data.pop('attributes', None)

        product = Product.objects.create(**validated_data)

        if product.category:
            cattegory_attributes = CategoryAttribute.objects.filter(category=product.category)
            for attribute in cattegory_attributes:
                ProductAttribute.objects.create(product=product, user_attribute=False, attribute=attribute.attribute,
                                                multiple=attribute.attribute.multiple)

        return product

    def update(self, instance, validated_data):

        attributes = validated_data.pop('attributes', None)

        # Product instance updating
        if instance.language_code != validated_data['language_code']:
            instance.translate(validated_data['language_code'])
        instance.product_group = validated_data['product_group']
        instance.category = validated_data['category']
        instance.suggested_category = validated_data['suggested_category']
        instance.model_number = validated_data['model_number']
        instance.brand_name = validated_data['brand_name']
        instance.origin = validated_data['origin']
        instance.unit_type = validated_data['unit_type']
        instance.published = validated_data['published']
        instance.price_from = validated_data['price_from']
        instance.price_to = validated_data['price_to']
        instance.discount_price_from = validated_data['discount_price_from']
        instance.discount_price_to = validated_data['discount_price_to']
        instance.deadline = validated_data['deadline']
        instance.discount = validated_data['discount']
        instance.one_price = validated_data['one_price']
        instance.currency = validated_data['currency']
        instance.name = validated_data['name']

        instance.short_description = validated_data['short_description']
        instance.price_conditions = validated_data['price_conditions']
        instance.link_to_buy = validated_data['link_to_buy']
        instance.packaging_and_delivery = validated_data['packaging_and_delivery']
        instance.tags = validated_data['tags']

        # print(instance.tags)
        instance.save()

        obj = Product.objects.get(pk=instance.pk)

        obj.tags.set(*validated_data['tags'], clear=False)

        ProductAttribute.objects.filter(product=instance).delete()
        if attributes:
            for attribute in attributes:
                values = attribute.pop('values', None)
                attribute_instance = ProductAttribute.objects.create(product=instance, **attribute)
                if values:
                    for value in values:
                        ProductAttributeValue.objects.create(product_attribute=attribute_instance, **value)

        return instance


class ProductShortSerializer(TranslatableModelSerializer):
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)
    images = ProductImageSerializer(many=True, read_only=False)
    eventsqty = ProductEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)

    currency_details = CurrencySerializer(source='currency', required=False, read_only=True)

    price_from_current_currency = serializers.SerializerMethodField()
    price_to_current_currency = serializers.SerializerMethodField()
    discount_price_from_current_currency = serializers.SerializerMethodField()
    discount_price_to_current_currency = serializers.SerializerMethodField()

    user_data = UserWithProfileMiddleSerializer(source='user', required=False, read_only=True)
    company_details = CompanyMiddleSerializer(source="company", required=False, read_only=True)
    company_default_details = CompanyMiddleSerializer(source="company", required=False, read_only=True, language='en')
    origin_details = CountrySerializer(source='origin', required=False, read_only=True)

    def get_price_from_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.price_from, obj.currency)

    def get_price_to_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.price_to, obj.currency)

    def get_discount_price_from_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.discount_price_from, obj.currency)

    def get_discount_price_to_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.discount_price_to, obj.currency)

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'category_details', 'images', 'name', 'product_or_service', 'unit_type',
            'unit_type_details', 'eventsqty', 'one_price',
            'price_from_current_currency', 'price_from', 'price_to', 'price_to_current_currency',
            'discount', 'deadline',
            'discount_price_from', 'discount_price_to',
            'discount_price_from_current_currency', 'discount_price_to_current_currency',
            'slug', 'user_data',
            'company_details',
            'company_default_details', 'currency_details', 'currency',
            'origin_details', 'published', 'deleted')

class ProductMiddleSerializer(TranslatableModelSerializer):
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)
    images = ProductImageSerializer(many=True, read_only=False)
    eventsqty = ProductEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)

    price_from_current_currency = serializers.SerializerMethodField()
    price_to_current_currency = serializers.SerializerMethodField()
    discount_price_from_current_currency = serializers.SerializerMethodField()
    discount_price_to_current_currency = serializers.SerializerMethodField()
    user_data = UserWithProfileSmallSerializer(source='user', required=False, read_only=True)
    company_details = CompanySmallSerializer(source="company", required=False, read_only=True)

    def get_price_from_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.price_from, obj.currency)

    def get_price_to_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.price_to, obj.currency)

    def get_discount_price_from_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.discount_price_from, obj.currency)

    def get_discount_price_to_current_currency(self, obj):
        return get_price_in_current_currency(self.context, obj.discount_price_to, obj.currency)

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'images', 'name', 'product_or_service', 'unit_type', 'user_data', 'company_details',
            'unit_type_details', 'eventsqty', 'one_price',
            'price_from_current_currency', 'price_from', 'price_to', 'price_to_current_currency',
            'discount', 'deadline', 'slug', 'company_details',
            'discount_price_from', 'discount_price_to',
            'discount_price_from_current_currency', 'discount_price_to_current_currency',
             'currency', 'published', 'deleted')


class FavoriteProductSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', required=False, read_only=True)
    product_default_details = ProductSerializer(source='product', required=False, read_only=True, language='en')

    class Meta:
        model = FavoriteProduct
        fields = ('id', 'product', 'user', 'product_details', 'product_default_details')
