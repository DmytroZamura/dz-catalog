from rest_framework import serializers
from .models import Company, CompanyIndustry, CompanyUser, CompanySize, CompanyType, CompanyCategory, CompanyFollower, \
    CompanyEventsQty, FavoriteCompany

from catalog.category.serializers import CategorySerializer
from catalog.general.serializers import CountrySerializer, CitySerializer, CitySmallSerializer, CountrySmallSerializer
from catalog.file.serializers import UserImageProfileSerializer
from catalog.user_profile.serializers import UserWithProfileSerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class CompanyTypeSerializer(TranslatableModelSerializer):
    class Meta:
        model = CompanyType
        fields = ('id', 'name', 'slug')


class CompanySizeSerializer(TranslatableModelSerializer):
    class Meta:
        model = CompanySize
        fields = ('id', 'name', 'slug')


class CompanyIndustrySerializer(TranslatableModelSerializer):
    class Meta:
        model = CompanyIndustry
        fields = ('id', 'name', 'slug')


class CompanyEventsQtySerializer(serializers.ModelSerializer):
    publications_total = serializers.SerializerMethodField()

    def get_publications_total(self, obj):
        return obj.jobposts + obj.publications + obj.offerings + obj.requests

    class Meta:
        model = CompanyEventsQty
        fields = (
            'followers', 'employees', 'students', 'publications_total', 'jobposts', 'publications', 'offerings',
            'requests', 'products', 'new_messages', 'new_job_responds', 'new_offering_reponds', 'new_request_responds',
            'new_customer_requests', 'open_customer_requests', 'your_open_supply_requests',
            'your_open_offering_responds', 'your_open_request_responds', 'reviews', 'rating', 'questions',
            'related_questions', 'related_reviews')


def get_follow_company_status(context, obj):
    status = False

    if context:
        if context['request'].user.id:
            status = CompanyFollower.objects.filter(user=context['request'].user, company=obj).exists()

    return status


def get_favorite_company_status(context, obj):
    status = False
    if context:
        if context['request'].user.id:
            status = FavoriteCompany.objects.filter(user=context['request'].user, company=obj).exists()
    return status


class CompanySerializer(TaggitSerializer, TranslatableModelSerializer):
    logo_details = UserImageProfileSerializer(source='logo', required=False, read_only=True)
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)
    company_type_details = CompanyTypeSerializer(source='company_type', required=False, read_only=True)
    company_industry_details = CompanyIndustrySerializer(source='company_industry', required=False, read_only=True)
    company_size_details = CompanySizeSerializer(source='company_size', required=False, read_only=True)
    follow_status = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    eventsqty = CompanyEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)

    favorite_status = serializers.SerializerMethodField()
    admin_status = serializers.SerializerMethodField()

    # business_email = serializers.SerializerMethodField()
    # sales_email = serializers.SerializerMethodField()
    #
    # phone_number = serializers.SerializerMethodField()
    #
    # def get_business_email(self, obj):
    #     email = ''
    #     if self.context:
    #         if self.context['request'].user.id:
    #             email = obj.business_email
    #     return email
    #
    # def get_sales_email(self, obj):
    #     email = ''
    #     if self.context:
    #         if self.context['request'].user.id:
    #             email = obj.sales_email
    #     return email
    #
    # def get_phone_number(self, obj):
    #     phone = ''
    #     if self.context:
    #         if self.context['request'].user.id:
    #             phone = obj.phone_number
    #     return phone

    def get_admin_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = CompanyUser.objects.filter(user=self.context['request'].user, company=obj,
                                                    admin=True).exists()
        return status

    def get_follow_status(self, obj):
        return get_follow_company_status(self.context, obj)

    def get_favorite_status(self, obj):
        return get_favorite_company_status(self.context, obj)

    class Meta:
        model = Company
        fields = (
            'id', 'headline', 'slug', 'name', 'eventsqty', 'country', 'country_details', 'short_description', 'logo',
            'logo_details', 'website', 'seo_title', 'seo_description',
            'linkedin', 'company_industry', 'company_industry_details', 'company_type', 'company_type_details',
            'follow_status', 'favorite_status',
            'company_size', 'company_size_details', 'city', 'city_details', 'city_name', 'address', 'postal_code',
            'phone_number', 'admin_status',
            'sales_email', 'business_email', 'foundation_year', 'language_code', 'tags', 'deleted', 'create_date',
            'update_date')

    read_only_fields = ('create_date', 'update_date',)


class CompanyShortSerializer(TranslatableModelSerializer):
    logo_details = UserImageProfileSerializer(source='logo', required=False, read_only=True)
    company_industry_details = CompanyIndustrySerializer(source='company_industry', required=False, read_only=True)
    company_type_details = CompanyTypeSerializer(source='company_type', required=False, read_only=True)

    company_size_details = CompanySizeSerializer(source='company_size', required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)

    eventsqty = CompanyEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    follow_status = serializers.SerializerMethodField()
    favorite_status = serializers.SerializerMethodField()

    def get_follow_status(self, obj):
        return get_follow_company_status(self.context, obj)

    def get_favorite_status(self, obj):
        return get_favorite_company_status(self.context, obj)

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'slug', 'country_details', 'city_details', 'headline', 'logo', 'logo_details',
            'company_industry', 'company_industry_details', 'company_type', 'company_type_details', 'company_size',
            'company_size_details', 'foundation_year', 'eventsqty', 'follow_status', 'favorite_status', 'deleted')


class CompanyMiddleSerializer(TranslatableModelSerializer):
    logo_details = UserImageProfileSerializer(source='logo', required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)

    eventsqty = CompanyEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    follow_status = serializers.SerializerMethodField()

    def get_follow_status(self, obj):
        return get_follow_company_status(self.context, obj)

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'slug', 'country_details', 'city_details', 'headline', 'logo', 'logo_details',
            'company_industry', 'company_type', 'company_size',
            'foundation_year', 'eventsqty', 'follow_status', 'deleted')


class CompanySmallSerializer(TranslatableModelSerializer):
    logo_details = UserImageProfileSerializer(source='logo', required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)

    eventsqty = CompanyEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)

    class Meta:
        model = Company
        fields = (
            'id', 'name', 'slug', 'headline', 'logo', 'logo_details',
            'company_industry', 'company_type', 'company_size', 'country_details', 'city_details',
            'foundation_year', 'eventsqty', 'deleted')


class CompanyNameSerializer(TranslatableModelSerializer):
    class Meta:
        model = Company
        fields = (
            'id', 'name', 'headline')


class CompanyCategorySerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', required=False, read_only=True)

    class Meta:
        model = CompanyCategory
        fields = ('id', 'company', 'category', 'category_details', 'company_category', 'child_qty')


class CompanyUserSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)
    company_details = CompanyShortSerializer(source='company', read_only=True, required=False, language='en')

    class Meta:
        model = CompanyUser
        fields = ('id', 'company', 'company_details', 'user', 'user_details', 'admin', 'sales', 'supply',)


class CompanyFollowerSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', read_only=True, required=False, language='en')
    company_details = CompanyShortSerializer(source='company', read_only=True, required=False)

    class Meta:
        model = CompanyFollower
        fields = ('id', 'company', 'company_details', 'company_default_details', 'user', 'user_details',)


class FavoriteCompanySerializer(serializers.ModelSerializer):
    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', read_only=True, required=False, language='en')

    class Meta:
        model = FavoriteCompany
        fields = ('id', 'company', 'user', 'company_details', 'company_default_details')
