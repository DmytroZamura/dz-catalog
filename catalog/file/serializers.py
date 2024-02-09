from rest_framework import serializers
from .models import *
from sorl.thumbnail import get_thumbnail


class FileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.file_url)
        else:
            return None

    class Meta:
        model = File
        fields = ('id', 'user_id', 'name', 'type', 'create_date', 'file_url')
        read_only_fields = ('create_date',)


class UserImageSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.file_url)
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '100x100', crop='center', quality=99).url
            return img
        else:
            return None


    medium_image_url = serializers.SerializerMethodField()

    def get_medium_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '900', crop='top', quality=95).url
            return img
        else:
            return None

    class Meta:
        model = UserImage
        fields = ('id', 'user_id', 'name', 'type', 'create_date', 'file_url', 'medium_image_url', 'small_image_url')
        read_only_fields = ('create_date',)


class UserImageSimpleSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.file_url)
        else:
            return None



    class Meta:
        model = UserImage
        fields = ('id', 'user_id', 'name', 'type', 'create_date', 'file_url')
        read_only_fields = ('create_date',)


class UserImageProfileSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.file_url)
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '80x80', crop='center', quality=99).url
            return img
        else:
            return None

    class Meta:
        model = UserImage
        fields = ('id', 'user_id', 'name', 'type', 'create_date', 'file_url', 'small_image_url')
        read_only_fields = ('create_date',)


class UserImageProductSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.file_url)
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '100x100', crop='center', quality=99).url
            return img
        else:
            return None

    medium_image_url = serializers.SerializerMethodField()

    def get_medium_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '350x350', crop='center', quality=90).url
            return img
        else:
            return None

    class Meta:
        model = UserImage
        fields = ('id', 'user_id', 'name', 'type', 'create_date', 'file_url', 'small_image_url', 'medium_image_url')
        read_only_fields = ('create_date',)


class UserImagePostSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.file_url)
        else:
            return None

    small_image_url = serializers.SerializerMethodField()

    def get_small_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '200x200', crop='top', quality=90).url
            return img
        else:
            return None

    medium_image_url = serializers.SerializerMethodField()

    def get_medium_image_url(self, obj):
        if self.context:
            img = get_thumbnail(obj.file, '700', crop='top', quality=95).url
            return img
        else:
            return None

    class Meta:
        model = UserImage
        fields = ('id', 'user_id', 'name', 'type', 'create_date', 'file_url', 'small_image_url', 'medium_image_url')
        read_only_fields = ('create_date',)
