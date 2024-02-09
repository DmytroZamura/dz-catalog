from rest_framework import serializers
from .models import Community, CommunityMember, CommunityInvitation, CommunityCompany, CommunityCategory, \
    CommunityEventsQty

from catalog.category.serializers import CategorySerializer
from catalog.general.serializers import CountrySerializer, CitySerializer
from catalog.company.serializers import CompanySerializer
from catalog.file.serializers import UserImageProfileSerializer
from catalog.user_profile.serializers import UserWithProfileSerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class CommunityEventsQtySerializer(serializers.ModelSerializer):
    publications_total = serializers.SerializerMethodField()

    def get_publications_total(self, obj):
        return obj.jobposts + obj.publications + obj.offerings + obj.requests

    class Meta:
        model = CommunityEventsQty
        fields = (
            'members', 'companies', 'publications_total', 'jobposts', 'publications', 'offerings',
            'requests', 'invitations', 'reviews', 'questions')


class CommunitySerializer(TaggitSerializer, TranslatableModelSerializer):
    image_details = UserImageProfileSerializer(source='image', required=False, read_only=True)
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)
    owner_details = UserWithProfileSerializer(source='owner', required=False, read_only=True)
    tags = TagListSerializerField(required=False)
    eventsqty = CommunityEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    member_status = serializers.SerializerMethodField()
    admin_status = serializers.SerializerMethodField()
    invitation_status = serializers.SerializerMethodField()

    def get_member_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = CommunityMember.objects.filter(user=self.context['request'].user, community=obj).exists()
        return status

    def get_admin_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = CommunityMember.objects.filter(user=self.context['request'].user, community=obj,
                                                        admin=True).exists()
        return status

    def get_invitation_status(self, obj):
        status = None
        if self.context:
            if self.context['request'].user.id:
                try:
                    invitation = CommunityInvitation.objects.get(user=self.context['request'].user, community=obj, company__isnull=True)
                    if invitation.pending:
                        if not invitation.user_acceptance:
                            status = 'pending'
                        else:
                            status = 'acceptance'

                except CommunityInvitation.DoesNotExist:
                    pass
        return status

    class Meta:
        model = Community
        fields = (
            'id', 'name', 'description', 'rules', 'owner', 'owner_details', 'image', 'image_details', 'open',
            'show_products', 'eventsqty',
            'moderator_check_invite', 'local_community', 'tags', 'member_status', 'admin_status', 'invitation_status',
            'country', 'country_details', 'city', 'city_details', 'create_date', 'language_code', 'deleted')

    read_only_fields = ('create_date',)


class CommunityShortSerializer(TranslatableModelSerializer):
    image_details = UserImageProfileSerializer(source='image', required=False, read_only=True)
    class Meta:
        model = Community
        fields = (
            'id', 'name', 'open', 'image_details', 'deleted')


class CommunityCategorySerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', required=False, read_only=True)

    class Meta:
        model = CommunityCategory
        fields = ('id', 'community', 'category', 'category_details', 'community_category', 'child_qty')


class CommunityMemberSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = CommunityMember
        fields = ('id', 'community', 'user', 'user_details', 'admin')


class CommunityCompanySerializer(serializers.ModelSerializer):
    company_details = CompanySerializer(source='company', read_only=True, required=False)
    company_default_details = CompanySerializer(source='company', read_only=True, required=False, language='en')

    class Meta:
        model = CommunityCompany
        fields = ('id', 'community', 'company', 'company_details', 'company_default_details', 'create_date')


class CommunityInvitationSerializer(serializers.ModelSerializer):
    company_details = CompanySerializer(source='company', read_only=True, required=False)
    company_default_details = CompanySerializer(source='company', read_only=True, required=False, language='en')
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = CommunityInvitation
        fields = ('id', 'community', 'company', 'company_details', 'company_default_details', 'user', 'user_details',
                  'message', 'pending', 'accepted', 'user_acceptance', 'accepted_by_user', 'create_date')
