from rest_framework import serializers
from .models import UserProfile, UserProfileCountryInterest, UserProfileCategory, UserProfileFollower, \
    UserProfileEventsQty, Resume
from django.contrib.auth.models import User
from catalog.general.serializers import LanguageSerializer, CitySerializer, CountrySerializer, CurrencySerializer, \
    CitySmallSerializer, CountrySmallSerializer
from catalog.file.serializers import UserImageProfileSerializer
from catalog.category.serializers import CategorySerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer
from catalog.file.serializers import FileSerializer


class UserProfileEventsQtySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfileEventsQty
        fields = (
            'followers', 'following', 'jobposts', 'publications', 'offerings', 'requests', 'products', 'notifications',
            'new_messages', 'new_job_responds', 'new_offering_reponds', 'new_request_responds',
            'new_customer_requests', 'open_customer_requests', 'your_open_supply_requests',
            'your_open_offering_responds', 'your_open_request_responds', 'your_open_job_responds', 'favorite_posts',
            'favorite_companies', 'favorite_products', 'favorite_communities', 'favorite_tags', 'reviews', 'rating',
            'questions', 'related_questions', 'related_reviews')


def get_follow_profile_status(context, profile):
    status = False

    if context:

        if context['request'].user.id:
            status = UserProfileFollower.objects.filter(user=context['request'].user, profile=profile).exists()

    return status


def get_following_profile_status(context, profile):
    status = False

    if context:

        if context['request'].user.id:
            status = UserProfileFollower.objects.filter(user=profile.user,
                                                        profile__user=context['request'].user).exists()

    return status


class UserProfileSerializer(TaggitSerializer, TranslatableModelSerializer):
    language_details = LanguageSerializer(source='interface_lang', required=False, read_only=True)
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)
    img_details = UserImageProfileSerializer(source='img', required=False, read_only=True)
    tags = TagListSerializerField(required=False)
    eventsqty = UserProfileEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    follow_status = serializers.SerializerMethodField()
    following_status = serializers.SerializerMethodField()

    def get_follow_status(self, obj):
        status = get_follow_profile_status(self.context, obj)

        return status

    def get_following_status(self, obj):
        status = get_following_profile_status(self.context, obj)
        return status

    class Meta:
        model = UserProfile
        fields = (
        'id', 'user_id', 'has_companies', 'contact_email', 'nickname', 'slug', 'first_name', 'last_name', 'job_title',
        'short_description', 'contact_phone', 'skype', 'website', 'headline', 'tags', 'eventsqty',
        'follow_status', 'following_status', 'interface_lang', 'country', 'language_details',
        'default_currency', 'is_active', 'deleted', 'settings_checked', 'notifications_sound',
        'message_sound',
        'country_details', 'city', 'city_details', 'city_name', 'img', 'img_details', 'tester', 'language_code')
        read_only_fields = ('slug', 'default_currency', 'notifications_sound', 'message_sound')


class UserSettingsSerializer(TranslatableModelSerializer):
    language_details = LanguageSerializer(source='interface_lang', required=False, read_only=True)
    default_currency_details = CurrencySerializer(source='default_currency', required=False, read_only=True)
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)

    email = serializers.SerializerMethodField()

    def get_email(self, obj):
        email = ''
        if self.context:
            if self.context['request'].user.id:
                email = obj.email
        return email

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user_id', 'email', 'nickname', 'slug', 'settings_checked', 'country', 'country_details', 'city',
            'city_details',
            'interface_lang', 'language_details', 'default_currency', 'default_currency_details', 'notifications_sound',
            'message_sound', 'notifications_email',
            'message_email')


class UserProfileShortSerializer(TranslatableModelSerializer):
    img_details = UserImageProfileSerializer(source='img', required=False, read_only=True)
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)
    eventsqty = UserProfileEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    follow_status = serializers.SerializerMethodField()
    following_status = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        name = ''
        if obj.first_name:
            name = obj.first_name
        if obj.last_name:
            name = name + ' ' + obj.last_name

        return name

    def get_follow_status(self, obj):
        status = get_follow_profile_status(self.context, obj)

        return status

    def get_following_status(self, obj):
        status = get_following_profile_status(self.context, obj)
        return status

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user_id', 'nickname', 'eventsqty', 'country_details', 'city_details', 'slug', 'job_title',
            'first_name', 'headline', 'full_name', 'is_active', 'deleted',
            'last_name', 'img_details', 'follow_status', 'following_status')
        read_only_fields = ('slug',)


class UserProfileMiddleSerializer(TranslatableModelSerializer):
    img_details = UserImageProfileSerializer(source='img', required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)
    eventsqty = UserProfileEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    follow_status = serializers.SerializerMethodField()
    following_status = serializers.SerializerMethodField()

    def get_follow_status(self, obj):
        status = get_follow_profile_status(self.context, obj)

        return status

    def get_following_status(self, obj):
        status = get_following_profile_status(self.context, obj)
        return status

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user_id', 'nickname', 'eventsqty', 'country_details', 'city_details', 'slug', 'job_title',
            'first_name', 'headline', 'full_name', 'is_active', 'deleted',
            'last_name', 'img_details', 'follow_status', 'following_status')
        read_only_fields = ('slug',)


class UserProfileSmallSerializer(TranslatableModelSerializer):
    img_details = UserImageProfileSerializer(source='img', required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)
    eventsqty = UserProfileEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = (
            'id', 'user_id', 'nickname', 'slug', 'job_title',
            'first_name', 'full_name', 'headline', 'is_active', 'deleted', 'country_details', 'city_details',
            'last_name', 'img_details', 'eventsqty')
        read_only_fields = ('slug',)


class UserWithProfileSerializer(serializers.ModelSerializer):
    user_profile = UserProfileShortSerializer(required=False, read_only=True)
    user_profile_default = UserProfileShortSerializer(source='user_profile', required=False, read_only=True,
                                                      language='en')

    class Meta:
        model = User
        fields = ('id', 'user_profile', 'user_profile_default')


class UserWithProfileMiddleSerializer(serializers.ModelSerializer):
    user_profile = UserProfileMiddleSerializer(required=False, read_only=True)
    user_profile_default = UserProfileMiddleSerializer(source='user_profile', required=False, read_only=True,
                                                       language='en')

    class Meta:
        model = User
        fields = ('id', 'user_profile', 'user_profile_default')


class UserWithProfileSmallSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSmallSerializer(required=False, read_only=True)
    user_profile_default = UserProfileSmallSerializer(source='user_profile', required=False, read_only=True,
                                                      language='en')

    class Meta:
        model = User
        fields = ('id', 'user_profile', 'user_profile_default')


class UserProfileCategorySerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', required=False, read_only=True)

    class Meta:
        model = UserProfileCategory
        fields = (
            'id', 'profile', 'category', 'category_details', 'interest', 'profile_category', 'child_qty',
            'products_qty')


class UserProfileCountryInterestSerializer(serializers.ModelSerializer):
    country_details = CountrySerializer(source='country', required=False, read_only=True)

    class Meta:
        model = UserProfileCountryInterest
        fields = ('id', 'profile', 'country', 'country_details')


class UserProfileFollowerSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)
    profile_default_details = UserProfileShortSerializer(source='profile', read_only=True, required=False,
                                                         language='en')
    profile_details = UserProfileShortSerializer(source='profile', read_only=True, required=False)

    class Meta:
        model = UserProfileFollower
        fields = ('id', 'profile', 'profile_details', 'profile_default_details', 'user', 'user_details')


class ResumeSerializer(serializers.ModelSerializer):
    file_details = FileSerializer(source='file', required=False, read_only=True)

    class Meta:
        model = Resume
        fields = (
            'id', 'profile', 'create_date', 'show_in_profile', 'file', 'file_details')
