from rest_framework import serializers
from .models import Post, PostCategory, PostType, PostRequest, PostRequestPosition, PostDocument, PostImage, \
    PostAttribute, PostAttributeValue, PostOffering, PostLike, PostEventsQty, PostCommentUrlPreview, \
    PostCommentLike, PostCommentEventsQty, PostComment, PostJob, Applicant, ApplicantChat, ApplicantStatus, \
    PostRespondChat, PostRespondDocument, PostRespondStatus, PostRespond, FavoritePost, PostReview, PostOption, \
    PostOptionVote, Article, PostSEOData, RelatedPost
from catalog.general.models import Language
from catalog.company.models import CompanyUser
from catalog.community.models import CommunityMember
from catalog.user_profile.serializers import UserWithProfileSerializer, UserWithProfileMiddleSerializer, \
    UserWithProfileSmallSerializer
from catalog.category.serializers import CategorySerializer, SuggestedCategorySerializer
from catalog.product.serializers import ProductShortSerializer, ProductMiddleSerializer
from catalog.company.serializers import CompanyShortSerializer, CompanySmallSerializer, CompanyMiddleSerializer
from catalog.community.serializers import CommunityShortSerializer
from catalog.general.serializers import CountrySerializer, CountrySmallSerializer, UnitTypeSerializer, \
    CurrencySerializer, CitySerializer, \
    JobTypeSerializer, JobFunctionSerializer, SeniorityLabelSerializer, CitySmallSerializer, LanguageSerializer
from catalog.messaging.serializers import ChatSerializer
from catalog.file.serializers import FileSerializer, UserImagePostSerializer, UserImageSimpleSerializer
from catalog.attribute.serializers import AttributeSerializer, AttributeValueSerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from catalog.hashtag.serializers import TagSerializer
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class PostImageSerializer(serializers.ModelSerializer):
    file_details = UserImagePostSerializer(source='file', required=False, read_only=True)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = PostImage
        fields = (
            'id', 'file', 'file_details', 'comment')


class PostCommentUrlPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentUrlPreview
        fields = ('url', 'image', 'title', 'site_name', 'description')


class PostEventsQtySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostEventsQty
        fields = (
            'comments', 'likes', 'shares', 'applicants', 'impressions', 'views',
            'user_impressions', 'user_views', 'engagements',
            'new_applicants', 'responds', 'new_responds', 'votes')


class PostLikeSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = PostLike
        fields = (
            'id', 'post', 'user', 'user_data', 'create_date')

        read_only_fields = ('create_date',)


class PostLikeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostLike
        fields = (
            'id', 'post', 'user', 'create_date')

        read_only_fields = ('create_date',)


class PostCommentLikeSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = PostCommentLike
        fields = (
            'id', 'comment', 'user', 'user_data', 'create_date')

        read_only_fields = ('create_date',)


class PostCommentLikeSmallSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentLike
        fields = (
            'id', 'comment', 'user', 'create_date')

        read_only_fields = ('create_date',)


class PostCommentEventsQtySerializer(serializers.ModelSerializer):
    class Meta:
        model = PostCommentEventsQty
        fields = (
            'comment', 'likes', 'comments')


class PostCommentSerializer(serializers.ModelSerializer):
    urlpreview = PostCommentUrlPreviewSerializer(many=False, required=False, allow_null=True)
    image_details = UserImageSimpleSerializer(source='image', required=False, read_only=True)
    eventsqty = PostCommentEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)
    like_status = serializers.SerializerMethodField()
    can_delete_status = serializers.SerializerMethodField()

    def get_can_delete_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = obj.post.user == self.context['request'].user
                if obj.post.community and not status:
                    status = CommunityMember.objects.filter(user=self.context['request'].user,
                                                            community=obj.post.community,
                                                            admin=True).exists()
        return status

    def get_like_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = PostCommentLike.objects.filter(user=self.context['request'].user, comment=obj).exists()
        return status

    class Meta:
        model = PostComment
        fields = (
            'id', 'post', 'user', 'user_data', 'reply_to', 'parent', 'text', 'image', 'image_details', 'update_date',
            'urlpreview',
            'eventsqty', 'like_status', 'can_delete_status')
        read_only_fields = ('update_date',)

    def create(self, validated_data):

        urlpreview = validated_data.pop('urlpreview', None)

        comment = PostComment.objects.create(**validated_data)

        if urlpreview:
            PostCommentUrlPreview.objects.create(comment=comment, **urlpreview)

        return comment

    def update(self, instance, validated_data):

        urlpreview = validated_data.pop('urlpreview', None)

        # Comment instance updating
        instance.text = validated_data['text']
        instance.image = validated_data['image']
        instance.save()

        # UrlPreview instance updating
        if urlpreview:
            try:
                urlpreview_instance = PostCommentUrlPreview.objects.get(comment=instance)
                urlpreview_instance.url = urlpreview['url']
                urlpreview_instance.title = urlpreview['title']
                urlpreview_instance.site_name = urlpreview['site_name']
                urlpreview_instance.description = urlpreview['description']
                urlpreview_instance.image = urlpreview['image']
                urlpreview_instance.save()
            except PostCommentUrlPreview.DoesNotExist:
                PostCommentUrlPreview.objects.create(comment=instance, **urlpreview)
        else:
            PostCommentUrlPreview.objects.filter(comment=instance).delete()
        return instance


class PostCommentSmallSerializer(serializers.ModelSerializer):
    image_details = UserImageSimpleSerializer(source='image', required=False, read_only=True)

    class Meta:
        model = PostComment
        fields = (
            'id', 'post', 'user', 'parent', 'text', 'image', 'image_details', 'update_date',)
        read_only_fields = ('update_date',)

    def create(self, validated_data):

        urlpreview = validated_data.pop('urlpreview', None)

        comment = PostComment.objects.create(**validated_data)

        if urlpreview:
            PostCommentUrlPreview.objects.create(comment=comment, **urlpreview)

        return comment

    def update(self, instance, validated_data):

        urlpreview = validated_data.pop('urlpreview', None)

        # Comment instance updating
        instance.text = validated_data['text']
        instance.image = validated_data['image']
        instance.save()

        # UrlPreview instance updating
        if urlpreview:
            try:
                urlpreview_instance = PostCommentUrlPreview.objects.get(comment=instance)
                urlpreview_instance.url = urlpreview['url']
                urlpreview_instance.title = urlpreview['title']
                urlpreview_instance.site_name = urlpreview['site_name']
                urlpreview_instance.description = urlpreview['description']
                urlpreview_instance.image = urlpreview['image']
                urlpreview_instance.save()
            except PostCommentUrlPreview.DoesNotExist:
                PostCommentUrlPreview.objects.create(comment=instance, **urlpreview)
        else:
            PostCommentUrlPreview.objects.filter(comment=instance).delete()
        return instance


class PostTypeSerializer(TranslatableModelSerializer):
    class Meta:
        model = PostType
        fields = ('id', 'code', 'name', 'name_plural', 'feed_id')


class PostRequestSerializer(serializers.ModelSerializer):
    price_currency_details = CurrencySerializer(source='price_currency', required=False, read_only=True)

    class Meta:
        model = PostRequest
        fields = (
            'price_currency', 'price_currency_details', 'deadline', 'delivery_address')


class PostOfferingSerializer(serializers.ModelSerializer):
    price_currency_details = CurrencySerializer(source='price_currency', required=False, read_only=True)
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)

    class Meta:
        model = PostOffering
        fields = (
            'type', 'unit_type', 'unit_type_details', 'price_currency', 'price_currency_details', 'one_price', 'price',
            'price_usd', 'price_from', 'price_usd_from',
            'discount',
            'discount_price_from', 'discount_price', 'discount_price_usd_from', 'discount_price_usd')


class PostReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReview
        fields = (
            'advantages', 'disadvantages', 'rating')


class PostJobSerializer(serializers.ModelSerializer):
    salary_currency_details = CurrencySerializer(source='salary_currency', required=False, read_only=True)
    job_type_details = JobTypeSerializer(source='job_type', required=False, read_only=True)
    job_function_details = JobFunctionSerializer(source='job_function', required=False, read_only=True)
    seniority_details = SeniorityLabelSerializer(source='seniority', required=False, read_only=True)

    class Meta:
        model = PostJob
        fields = (
            'job_type', 'job_type_details', 'job_function', 'job_function_details', 'seniority', 'seniority_details',
            'salary_currency', 'salary_currency_details', 'salary', 'resume_required')


class ArticleShortSerializer(TranslatableModelSerializer):
    class Meta:
        model = Article
        fields = (

            'title', 'title_draft', 'description')


class RelatedPostPreviewSerializer(serializers.ModelSerializer):
    type_details = PostTypeSerializer(source='type', required=False, read_only=True)
    article = ArticleShortSerializer(many=False, required=False, allow_null=True)
    images = PostImageSerializer(many=True, required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    post_request = PostRequestSerializer(many=False, required=False, allow_null=True)
    post_offering = PostOfferingSerializer(many=False, required=False, allow_null=True)
    post_job = PostJobSerializer(many=False, required=False, allow_null=True)

    class Meta:
        model = Post
        fields = (
            'id', 'site_name', 'country_details', 'city_details', 'category_details', 'type', 'type_details', 'title',
            'description', 'post_title', 'comment', 'create_date', 'user', 'company',
            'slug', 'article', 'images', 'image_url', 'url', 'deadline',
            'post_request', 'post_offering', 'post_job', 'deleted', 'published')


class PostShortSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileSmallSerializer(source='user', required=False, read_only=True)
    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', required=False, read_only=True, language='en')
    type_details = PostTypeSerializer(source='type', required=False, read_only=True)
    article = ArticleShortSerializer(many=False, required=False, allow_null=True)
    images = PostImageSerializer(many=True, required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    post_request = PostRequestSerializer(many=False, required=False, allow_null=True)
    post_offering = PostOfferingSerializer(many=False, required=False, allow_null=True)
    post_job = PostJobSerializer(many=False, required=False, allow_null=True)
    comment = serializers.SerializerMethodField()

    def get_comment(self, obj):
        comment = ''
        if obj.comment:
            comment = (obj.comment[:300] + '..') if len(obj.comment) > 300 else obj.comment
        return comment

    description = serializers.SerializerMethodField()

    def get_description(self, obj):
        description = ''
        if obj.description:
            description = (obj.description[:300] + '..') if len(obj.description) > 300 else obj.description
        return description

    class Meta:
        model = Post
        fields = (
            'id', 'site_name', 'country_details', 'city_details', 'category_details', 'type', 'type_details',
            'title', 'description', 'post_title', 'comment', 'create_date', 'user', 'company', 'user_data',
            'company_details', 'slug', 'article', 'images', 'image_url', 'url', 'deadline', 'promotion',
            'promotion_grade',
            'promotion_date',
            'company_default_details', 'post_request', 'post_offering', 'post_job', 'deleted', 'published')


class RelatedPostSerializer(serializers.ModelSerializer):
    related_post_details = PostShortSerializer(source='related_post', required=False, read_only=True)

    class Meta:
        model = RelatedPost
        fields = ('id', 'post', 'related_post', 'related_post_details', 'create_date')


class PostMiddleSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)
    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', required=False, read_only=True, language='en')
    type_details = PostTypeSerializer(source='type', required=False, read_only=True)
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)
    eventsqty = PostEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    tags = TagListSerializerField(required=False)
    related_posts = RelatedPostSerializer(many=True, required=False)
    like_status = serializers.SerializerMethodField()
    admin_status = serializers.SerializerMethodField()
    favorite_status = serializers.SerializerMethodField()

    def get_favorite_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = FavoritePost.objects.filter(user=self.context['request'].user, post=obj).exists()
        return status

    def get_like_status(self, obj):
        status = False
        if self.context:

            if self.context['request'].user.id:
                status = PostLike.objects.filter(user=self.context['request'].user, post=obj).exists()
        return status

    def get_admin_status(self, obj):
        status = False
        if self.context:

            if self.context['request'].user.id:
                status = self.context['request'].user.id == obj.user_id

                if not status and obj.company:
                    status = CompanyUser.objects.filter(user=self.context['request'].user, company=obj.company).exists()

        return status

    class Meta:
        model = Post
        fields = (
            'id', 'type', 'type_details', 'post_title', 'create_date', 'user', 'company', 'user_data',
            'company_details', 'company_default_details', 'slug', 'category', 'category_details', 'country',
            'country_details', 'tags', 'related_posts', 'promotion', 'promotion_grade', 'promotion_date',
            'city', 'city_details', 'eventsqty', 'like_status', 'admin_status', 'favorite_status',
            'deleted', 'published')


class ArticleSerializer(TaggitSerializer, TranslatableModelSerializer):
    default_lang_details = LanguageSerializer(source='default_lang', required=False, read_only=True)
    image_details = UserImagePostSerializer(source='image', required=False, read_only=True)
    image_draft_details = UserImagePostSerializer(source='image_draft', required=False, read_only=True)
    draft_category_details = CategorySerializer(source='draft_category', required=False, read_only=True)
    draft_country_details = CountrySmallSerializer(source='draft_country', required=False, read_only=True)
    draft_city_details = CitySmallSerializer(source='draft_city', required=False, read_only=True)
    post_details = PostMiddleSerializer(source='post', required=False, read_only=True)
    languages = serializers.SerializerMethodField()
    languages_to_add = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)

    def get_languages(self, obj):
        langs = obj.get_available_languages()

        languages = Language.objects.language().fallbacks('en').filter(code__in=langs)
        serializer = LanguageSerializer(languages, many=True)

        return serializer.data

    def get_languages_to_add(self, obj):
        langs = obj.get_available_languages()

        languages = Language.objects.language().fallbacks('en').filter(locale_lang=True).exclude(code__in=langs)
        serializer = LanguageSerializer(languages, many=True)

        return serializer.data

    class Meta:
        model = Article
        fields = ('post', 'post_details', 'draft_category', 'draft_category_details',
                  'draft_country', 'draft_country_details', 'draft_city', 'draft_city_details',
                  'default_lang', 'default_lang_details', 'image', 'image_details', 'image_draft',
                  'image_draft_details', 'tags',
                  'title', 'seo_title', 'description', 'text',
                  'title_draft', 'seo_title_draft', 'description_draft', 'text_draft', 'link_canonical_draft',
                  'link_canonical', 'to_publish',
                  'languages', 'languages_to_add',
                  'language_code')


class PostDocumentSerializer(serializers.ModelSerializer):
    file_details = FileSerializer(source='file', required=False, read_only=True)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = PostDocument
        fields = (
            'id', 'file', 'file_details')


class ApplicantStatusSerializer(TranslatableModelSerializer):
    class Meta:
        model = ApplicantStatus
        fields = ('id', 'code', 'name', 'icon', 'color_class')


class ApplicantChatSerializer(serializers.ModelSerializer):
    chat_details = ChatSerializer(source='chat', required=False, read_only=True)

    class Meta:
        model = ApplicantChat
        fields = (
            'applicant', 'chat', 'chat_details')


class PostRespondChatSerializer(serializers.ModelSerializer):
    chat_details = ChatSerializer(source='chat', required=False, read_only=True)

    class Meta:
        model = PostRespondChat
        fields = (
            'respond', 'chat', 'chat_details')


class ApplicantSerializer(serializers.ModelSerializer):
    resume_details = FileSerializer(source='resume', required=False, read_only=True)
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)
    chat_details = ApplicantChatSerializer(source='chat', required=False, read_only=True)
    post_details = PostShortSerializer(source='post', required=False, read_only=True)
    status_details = ApplicantStatusSerializer(source='status', required=False, read_only=True)

    class Meta:
        model = Applicant
        fields = (
            'id', 'post', 'user', 'user_details', 'post_details', 'create_date', 'chat_details',
            'update_date', 'resume', 'resume_details', 'salary_exp', 'contact_email', 'contact_phone', 'skype',
            'reviewed', 'status', 'status_details', 'cover_letter', 'comment', 'rating')


class PostRespondStatusSerializer(TranslatableModelSerializer):
    class Meta:
        model = PostRespondStatus
        fields = ('id', 'code', 'name', 'icon', 'color_class')


class PostRespondSerializer(serializers.ModelSerializer):
    user_details = UserWithProfileSerializer(source='user', required=False, read_only=True)
    chat_details = PostRespondChatSerializer(source='chat', required=False, read_only=True)
    post_details = PostShortSerializer(source='post', required=False, read_only=True)
    status_details = PostRespondStatusSerializer(source='status', required=False, read_only=True)
    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', required=False, read_only=True, language='en')
    currency_details = CurrencySerializer(source='currency', required=False, read_only=True)
    documents = PostDocumentSerializer(many=True, required=False)

    class Meta:
        model = PostRespond
        fields = (
            'id', 'post', 'user', 'user_details', 'company', 'company_details', 'company_default_details',
            'post_details', 'proposed_price', 'currency', 'currency_details',
            'create_date', 'chat_details', 'documents',
            'update_date', 'contact_email', 'contact_phone', 'skype',
            'reviewed', 'status', 'status_details', 'cover_letter', 'comment', 'rating')
        read_only_fields = ('create_date', 'update_date',)

    def create(self, validated_data):

        documents = validated_data.pop('documents', None)

        obj = PostRespond.objects.create(**validated_data)

        if documents:
            for document in documents:
                PostRespondDocument.objects.create(respond=obj, **document)

        return obj


class PostRequestPositionSerializer(serializers.ModelSerializer):
    unit_details = UnitTypeSerializer(source='unit', required=False, read_only=True)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = PostRequestPosition
        fields = (
            'id', 'index', 'name', 'unit', 'unit_details', 'quantity', 'comment')

        read_only_fields = ('index',)


class PostAttributeValueSerializer(serializers.ModelSerializer):
    value_list_details = AttributeValueSerializer(source='value_list', required=False, read_only=True)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = PostAttributeValue
        fields = (
            'id', 'value_string', 'value_number', 'value_integer', 'value_boolean', 'value_list', 'value_list_details')


class PostAttributeSerializer(serializers.ModelSerializer):
    attribute_details = AttributeSerializer(source='attribute', required=False, read_only=True)
    values = PostAttributeValueSerializer(many=True, required=False)
    id = serializers.IntegerField(required=False, read_only=False)

    class Meta:
        model = PostAttribute
        fields = ('id', 'attribute', 'attribute_details', 'name', 'user_attribute', 'multiple', 'values')


class RecursiveParentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.__class__(value, context=self.context)
        return serializer.data


class PostOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, read_only=False)
    votes_percent = serializers.SerializerMethodField()
    vote_status = serializers.SerializerMethodField()

    def get_vote_status(self, obj):
        status = False

        if self.context:
            if self.context['request'].user.id:
                status = PostOptionVote.objects.filter(user=self.context['request'].user, post=obj.post,
                                                       option=obj).exists()
        return status

    def get_votes_percent(self, obj):
        percent = 0
        if obj.post.eventsqty.votes > 0:
            percent = round((obj.votes / obj.post.eventsqty.votes) * 100, 0)
        return percent

    class Meta:
        model = PostOption
        fields = (
            'id', 'position', 'name', 'votes', 'votes_percent', 'vote_status')

        read_only_fields = ('votes',)


class PostOptionVoteSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = PostOptionVote
        fields = (
            'id', 'user', 'option', 'post', 'user_data', 'create_date')
        read_only_fields = ('create_date',)


class PostSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileMiddleSerializer(source='user', required=False, read_only=True)
    company_details = CompanyMiddleSerializer(source='company', required=False, read_only=True)

    community_details = CommunityShortSerializer(source='community', required=False, read_only=True)

    product_details = ProductMiddleSerializer(source='product', required=False, read_only=True)
    product_default_details = ProductMiddleSerializer(source='product', required=False, read_only=True, language='en')

    related_user_data = UserWithProfileMiddleSerializer(source='related_user', required=False, read_only=True)
    related_product_details = ProductMiddleSerializer(source='related_product', required=False, read_only=True,
                                                      language='')
    related_company_details = CompanyMiddleSerializer(source='related_company', required=False, read_only=True)

    related_product_default_details = ProductMiddleSerializer(source='related_product', required=False, read_only=True,
                                                              language='en')
    company_default_details = CompanyMiddleSerializer(source='company', required=False, read_only=True, language='en')

    community_default_details = CommunityShortSerializer(source='community', required=False, read_only=True,
                                                         language='en')
    related_company_default_details = CompanyMiddleSerializer(source='related_company', required=False, read_only=True,
                                                              language='en')

    type_details = PostTypeSerializer(source='type', required=False, read_only=True)
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    suggested_category_details = SuggestedCategorySerializer(source="suggested_category", required=False,
                                                             read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySmallSerializer(source='city', required=False, read_only=True)
    post_request = PostRequestSerializer(many=False, required=False, allow_null=True)
    post_offering = PostOfferingSerializer(many=False, required=False, allow_null=True)
    post_review = PostReviewSerializer(many=False, required=False, allow_null=True)
    post_job = PostJobSerializer(many=False, required=False, allow_null=True)
    article = ArticleShortSerializer(many=False, required=False, allow_null=True, read_only=True)
    documents = PostDocumentSerializer(many=True, required=False)
    post_options = PostOptionSerializer(many=True, required=False)
    images = PostImageSerializer(many=True, required=False)
    post_request_positions = PostRequestPositionSerializer(many=True, required=False)
    attributes = PostAttributeSerializer(many=True, required=False)
    eventsqty = PostEventsQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    shared_post_details = RecursiveParentSerializer(source='shared_post', required=False, read_only=True)
    tags = TagListSerializerField(required=False)
    like_status = serializers.SerializerMethodField()
    applicant_status = serializers.SerializerMethodField()
    responder_status = serializers.SerializerMethodField()
    admin_status = serializers.SerializerMethodField()
    can_delete_status = serializers.SerializerMethodField()
    favorite_status = serializers.SerializerMethodField()

    def get_favorite_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                status = FavoritePost.objects.filter(user=self.context['request'].user, post=obj).exists()
        return status

    def get_like_status(self, obj):
        status = False
        if self.context:

            if self.context['request'].user.id:
                status = PostLike.objects.filter(user=self.context['request'].user, post=obj).exists()
        return status

    def get_applicant_status(self, obj):
        status = False
        if self.context and obj.type.code == 'job':

            if self.context['request'].user.id:
                status = Applicant.objects.filter(user=self.context['request'].user, post=obj).exists()
        return status

    def get_responder_status(self, obj):
        status = False
        if self.context and (obj.type.code == 'offering' or obj.type.code == 'request'):

            if self.context['request'].user.id:
                status = PostRespond.objects.filter(user=self.context['request'].user, post=obj).exists()

        return status

    def get_admin_status(self, obj):
        status = False
        if self.context:

            if self.context['request'].user.id:
                status = self.context['request'].user.id == obj.user_id

                if not status and obj.company:
                    status = CompanyUser.objects.filter(user=self.context['request'].user, company=obj.company).exists()

        return status

    def get_can_delete_status(self, obj):
        status = False
        if self.context:
            if self.context['request'].user.id:
                if obj.community:
                    status = CommunityMember.objects.filter(user=self.context['request'].user, community=obj.community,
                                                            admin=True).exists()

        return status

    class Meta:
        model = Post
        fields = (
            'id', 'shared_post', 'shared_post_details', 'url', 'slug', 'site_name', 'is_video_url', 'type',
            'type_details', 'tags',
            'category', 'category_details', 'suggested_category', 'suggested_category_details',
            'country', 'admin_status', 'can_delete_status',
            'country_details', 'city', 'city_name', 'city_details', 'post_title', 'comment', 'title',
            'description', 'seo_title',
            'image_url', 'user_data', 'user', 'post_request', 'post_offering', 'post_job', 'post_review', 'article',
            'applicant_status',
            'responder_status',
            'documents', 'images', 'post_options',
            'post_request_positions',
            'attributes', 'eventsqty',
            'related_product', 'related_product_default_details', 'related_product_details',
            'company', 'company_details', 'company_default_details', 'product', 'product_details',
            'product_default_details', 'community', 'community_details', 'community_default_details',
            'related_user_data',
            'related_user', 'related_company', 'related_company_details', 'related_company_default_details',
            'promotion', 'promotion_grade', 'promotion_date',
            'published', 'multi_selection', 'deleted',
            'like_status', 'favorite_status', 'deadline', 'post_language',
            'create_date')
        read_only_fields = ('create_date', 'tags',)

    def create(self, validated_data):

        post_request = validated_data.pop('post_request', None)
        post_offering = validated_data.pop('post_offering', None)
        post_job = validated_data.pop('post_job', None)
        post_review = validated_data.pop('post_review', None)

        positions = validated_data.pop('post_request_positions', None)
        options = validated_data.pop('post_options', None)
        documents = validated_data.pop('documents', None)
        images = validated_data.pop('images', None)
        attributes = validated_data.pop('attributes', None)
        post = Post.objects.create(**validated_data)

        if post.type.code == 'request':
            if post_request:
                PostRequest.objects.create(post=post, **post_request)
            else:
                PostRequest.objects.create(post=post)

        if post.type.code == 'offering':
            if post_offering:
                PostOffering.objects.create(post=post, **post_offering)
            else:
                PostOffering.objects.create(post=post)

        if post.type.code == 'job':
            if post_job:
                PostJob.objects.create(post=post, **post_job)
            else:
                PostJob.objects.create(post=post)
        if post.type.code == 'review':
            print(post_review)
            if post_review:
                PostReview.objects.create(post=post, **post_review)
            else:
                PostReview.objects.create(post=post)

        if positions:
            for position in positions:
                PostRequestPosition.objects.create(post=post, **position)

        if documents:
            for document in documents:
                PostDocument.objects.create(post=post, **document)

        if options:
            for option in options:
                PostOption.objects.create(post=post, **option)

        if images:
            for image in images:
                PostImage.objects.create(post=post, **image)

        if attributes:
            for attribute in attributes:
                values = attribute.pop('values', None)
                attribute_instance = PostAttribute.objects.create(post=post, **attribute)
                if values:
                    for value in values:
                        PostAttributeValue.objects.create(post_attribute=attribute_instance, **value)
        return post

    def update(self, instance, validated_data):

        post_offering = validated_data.pop('post_offering', None)
        post_request = validated_data.pop('post_request', None)
        post_job = validated_data.pop('post_job', None)
        post_review = validated_data.pop('post_review', None)
        documents = validated_data.pop('documents', None)
        options = validated_data.pop('post_options', None)
        images = validated_data.pop('images', None)
        positions = validated_data.pop('post_request_positions', None)
        attributes = validated_data.pop('attributes', None)

        # Post instance updating
        instance.product = validated_data['product']
        instance.category = validated_data['category']
        instance.suggested_category = validated_data['suggested_category']
        instance.country = validated_data['country']
        instance.city = validated_data['city']
        instance.city_name = validated_data['city_name']
        instance.url = validated_data['url']
        instance.site_name = validated_data['site_name']
        instance.is_video_url = validated_data['is_video_url']
        instance.image_url = validated_data['image_url']
        instance.title = validated_data['title']
        instance.description = validated_data['description']
        instance.post_title = validated_data['post_title']
        instance.comment = validated_data['comment']
        instance.published = validated_data['published']
        instance.product = validated_data['product']
        instance.multi_selection = validated_data['multi_selection']
        instance.deadline = validated_data['deadline']
        instance.save()

        # Post Request instance updating
        if post_request and instance.type.code == 'request':
            post_request_instance = PostRequest.objects.get(post=instance)

            post_request_instance.price_currency = post_request['price_currency']
            post_request_instance.deadline = post_request['deadline']
            post_request_instance.delivery_address = post_request['delivery_address']

            post_request_instance.save()
            instance.post_request = post_request_instance

        # Post Offering instance updating
        if post_offering and instance.type.code == 'offering':
            post_offering_instance = PostOffering.objects.get(post=instance)
            post_offering_instance.type = post_offering['type']
            post_offering_instance.price_currency = post_offering['price_currency']
            post_offering_instance.price = post_offering['price']
            post_offering_instance.price_from = post_offering['price_from']
            post_offering_instance.discount = post_offering['discount']
            post_offering_instance.discount_price_from = post_offering['discount_price_from']
            post_offering_instance.discount_price = post_offering['discount_price']
            post_offering_instance.one_price = post_offering['one_price']
            post_offering_instance.unit_type = post_offering['unit_type']

            post_offering_instance.save()
            instance.post_offering = post_offering_instance

        # Post Review instance updating
        if post_review and instance.type.code == 'review':
            post_review_instance = PostReview.objects.get(post=instance)
            post_review_instance.rating = post_review['rating']
            post_review_instance.advantages = post_review['advantages']
            post_review_instance.disadvantages = post_review['disadvantages']

            post_review_instance.save()
            instance.post_review = post_review_instance

        # Post Job instance updating
        if post_job and instance.type.code == 'job':
            post_job_instance = PostJob.objects.get(post=instance)

            post_job_instance.job_type = post_job['job_type']
            post_job_instance.job_function = post_job['job_function']
            post_job_instance.seniority = post_job['seniority']
            post_job_instance.resume_required = post_job['resume_required']
            post_job_instance.salary_currency = post_job['salary_currency']
            post_job_instance.salary = post_job['salary']

            post_job_instance.save()
            instance.post_job = post_job_instance

        # Documents add or delete
        documents_ids = []
        for item in documents:
            item_id = item.get('id', None)

            if item_id is not None:
                documents_ids.append(item_id)
            else:
                document = PostDocument(post=instance, file=item['file'])
                document.save()
                documents_ids.append(document.id)

        for document in instance.documents.all():
            if document.id not in documents_ids:
                document.delete()

        # Images add or delete
        images_ids = []
        for item in images:

            item_id = item.get('id', None)

            if item_id is not None:
                images_ids.append(item_id)
            else:
                image = PostImage(post=instance, file=item['file'], comment=item.get('comment', None))
                image.save()
                images_ids.append(image.id)

        for image in instance.images.all():
            if image.id not in images_ids:
                image.delete()

        # Options add, update, delete
        options_ids = []
        for item in options:
            item_id = item.get('id', None)
            if item_id is not None:
                options_ids.append(item_id)
                option_instance = PostOption.objects.get(pk=item_id)
                option_instance.name = item['name']
                option_instance.position = item['position']
                option_instance.save()

            else:
                option = PostOption(post=instance, **item)
                option.save()
                options_ids.append(option.id)

        for option in instance.post_options.all():
            if option.id not in options_ids:
                option.delete()

        # Positions add, update, delete
        positions_ids = []
        for item in positions:
            item_id = item.get('id', None)
            if item_id is not None:
                positions_ids.append(item_id)
                position_instance = PostRequestPosition.objects.get(pk=item_id)
                position_instance.name = item['name']
                position_instance.unit = item['unit']
                position_instance.quantity = item['quantity']
                position_instance.comment = item['comment']
                position_instance.save()

            else:
                position = PostRequestPosition(post=instance, **item)
                position.save()
                positions_ids.append(position.id)

        for position in instance.post_request_positions.all():
            if position.id not in positions_ids:
                position.delete()

        PostAttribute.objects.filter(post=instance).delete()
        if attributes:
            for attribute in attributes:
                values = attribute.pop('values', None)
                attribute_instance = PostAttribute.objects.create(post=instance, **attribute)
                if values:
                    for value in values:
                        PostAttributeValue.objects.create(post_attribute=attribute_instance, **value)

        return instance


class PostSmallSerializer(serializers.ModelSerializer):
    type_details = PostTypeSerializer(source='type', required=False, read_only=True)
    images = PostImageSerializer(many=True, required=False, read_only=True)
    article = ArticleShortSerializer(many=False, required=False, allow_null=True)

    class Meta:
        model = Post
        fields = (
            'id', 'shared_post', 'url', 'site_name', 'is_video_url', 'type', 'type_details',

            'post_title', 'comment', 'title',
            'description',
            'image_url', 'user',
            'images',
            'article',

            'published', 'deleted', 'article',

            'create_date')
        read_only_fields = ('create_date',)


class PostPreviewSerializer(PostSerializer):
    related_posts = RelatedPostSerializer(many=True, required=False)

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ('related_posts',)


class PostCategorySerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(source='category', required=False, read_only=True)

    class Meta:
        model = PostCategory
        fields = ('id', 'post', 'category', 'category_details')


class FavoritePostSerializer(serializers.ModelSerializer):
    post_details = PostSerializer(source='post', required=False, read_only=True)

    class Meta:
        model = FavoritePost
        fields = ('id', 'post', 'user', 'post_details')


class PostSEOSerializer(serializers.ModelSerializer):
    post_type_details = PostTypeSerializer(source="post_type", required=False, read_only=True)
    category_details = CategorySerializer(source="category", required=False, read_only=True)
    country_details = CountrySmallSerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)
    job_type_details = JobTypeSerializer(source='job_type', required=False, read_only=True)
    job_function_details = JobFunctionSerializer(source='job_function', required=False, read_only=True)
    seniority_details = SeniorityLabelSerializer(source='seniority', required=False, read_only=True)

    class Meta:
        model = PostSEOData
        fields = ('id', 'filter_name', 'post_type_details', 'category_details', 'country_details',
                  'city_details', 'job_type_details', 'job_function_details',
                  'seniority_details')


class ActivityPostSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    verb = serializers.CharField()
    foreign_id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields["object"] = PostSerializer()


class ActivityPostActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    verb = serializers.CharField()
    foreign_id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields["target"] = PostSerializer()
        self.fields["actor"] = UserWithProfileMiddleSerializer()


class ActivityPostCommentsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    verb = serializers.CharField()
    foreign_id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields["target"] = PostSerializer()
        self.fields["object"] = PostCommentSerializer()
        self.fields["actor"] = UserWithProfileMiddleSerializer()


class ActivityTagedPostSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    verb = serializers.CharField()
    foreign_id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields["target"] = PostSerializer()
        self.fields["object"] = TagSerializer()


class ActivityFilterPostSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    verb = serializers.CharField()
    foreign_id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields["object"] = PostSerializer()
        self.fields["actor"] = PostSEOSerializer()


class ActivityCompanySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    verb = serializers.CharField()
    foreign_id = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.fields["target"] = CompanyShortSerializer(language='en')
        self.fields["actor"] = UserWithProfileMiddleSerializer()


class AggregatedPostsSerializer(serializers.Serializer):
    group = serializers.CharField()
    id = serializers.UUIDField()
    verb = serializers.CharField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    activity_count = serializers.IntegerField
    actor_count = serializers.IntegerField
    activities = ActivityPostSerializer(many=True)


class AggregatedFilterPostsSerializer(serializers.Serializer):
    group = serializers.CharField()
    id = serializers.UUIDField()
    verb = serializers.CharField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    activity_count = serializers.IntegerField
    actor_count = serializers.IntegerField
    activities = ActivityFilterPostSerializer(many=True)


class AggregatedPostsActivitiesSerializer(serializers.Serializer):
    group = serializers.CharField()
    id = serializers.UUIDField()
    verb = serializers.CharField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    activity_count = serializers.IntegerField
    actor_count = serializers.IntegerField
    activities = ActivityPostActivitySerializer(many=True)


class AggregatedPostsCommentsSerializer(serializers.Serializer):
    group = serializers.CharField()
    id = serializers.UUIDField()
    verb = serializers.CharField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    activity_count = serializers.IntegerField
    actor_count = serializers.IntegerField
    activities = ActivityPostCommentsSerializer(many=True)


class AggregatedTagedPostsSerializer(serializers.Serializer):
    group = serializers.CharField()
    id = serializers.UUIDField()
    verb = serializers.CharField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    activity_count = serializers.IntegerField
    actor_count = serializers.IntegerField
    activities = ActivityTagedPostSerializer(many=True)


class AggregatedCompanysSerializer(serializers.Serializer):
    group = serializers.CharField()
    id = serializers.UUIDField()
    verb = serializers.CharField()
    updated_at = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
    activity_count = serializers.IntegerField
    actor_count = serializers.IntegerField
    activities = ActivityCompanySerializer(many=True)
