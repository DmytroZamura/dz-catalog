
from rest_framework import serializers
from .models import *
from catalog.attribute.serializers import AttributeSerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from sorl.thumbnail import get_thumbnail




class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data

class RecursiveParentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data

class CategoryChildSetSerializer(TranslatableModelSerializer):
    children = RecursiveSerializer(source='child_set', many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

    def get_background_image_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.background_image_url)
        else:
            return None

    def get_image_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.image_url)
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context and obj.image:
            img = get_thumbnail(obj.image, '100x100', crop='top', quality=99).url
            return img
        else:
            return None

    class Meta:
        model = Category
        fields = ('id', 'name','description', 'parent', 'children', 'background_image_url', 'background_image', 'image', 'image_url', 'small_image_url', 'name_with_parent', 'slug', 'approved' , 'child_qty')






class CategorySerializer(TranslatableModelSerializer):
    image_url = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

    def get_background_image_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.background_image_url)
        else:
            return None

    def get_image_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.image_url)
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context and obj.image:
            img = get_thumbnail(obj.image, '100x100', crop='top', quality=99).url
            return img
        else:
            return None

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'parent', 'background_image_url', 'background_image',  'image', 'image_url', 'small_image_url', 'name_with_parent', 'slug', 'approved', 'child_qty', 'user')
        read_only_fields = ('slug', 'name_with_parent', 'child_qty', 'slug' , 'approved')


class CategoryParentSerializer(TranslatableModelSerializer):
    parent_details = RecursiveParentSerializer(source='parent', required=False, read_only=True)
    image_url = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

    def get_background_image_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.background_image_url)
        else:
            return None

    def get_image_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.image_url )
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context and obj.image:
            img = get_thumbnail(obj.image, '100x100', crop='top', quality=99).url
            return img
        else:
            return None

    class Meta:
        model = Category
        fields = ('id', 'name','description', 'parent', 'background_image_url', 'background_image', 'image', 'image_url', 'small_image_url', 'name_with_parent', 'slug', 'approved' , 'child_qty', 'parent_details')


class CategoryAttributeSerializer(serializers.ModelSerializer):
    attribute_details = AttributeSerializer(source='attribute', required=False, read_only=True)
    class Meta:
        model = CategoryAttribute
        fields = ('id', 'category', 'attribute', 'attribute_details', 'default_attribute', 'min', 'max', 'step')

class SuggestedCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SuggestedCategory
        fields = ('id', 'user', 'name', 'parent')

