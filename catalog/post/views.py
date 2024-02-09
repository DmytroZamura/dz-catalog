from .serializers import PostSerializer, PostCategorySerializer, PostTypeSerializer, PostCommentSerializer, \
    PostCommentLikeSerializer, PostLikeSerializer, ApplicantSerializer, ApplicantStatusSerializer, \
    PostRespondStatusSerializer, PostRespondSerializer, FavoritePostSerializer, PostOptionVoteSerializer, \
    AggregatedPostsSerializer, AggregatedPostsActivitiesSerializer, AggregatedTagedPostsSerializer, \
    AggregatedCompanysSerializer, ArticleSerializer, AggregatedFilterPostsSerializer, PostPreviewSerializer, \
    AggregatedPostsCommentsSerializer

from rest_framework import generics
from .models import Post, PostCategory, PostType, PostComment, PostCommentLike, PostLike, Applicant, ApplicantStatus, \
    PostRespond, PostRespondStatus, FavoritePost, PostOptionVote, Article, PostSEOData, PostSEODataFollower, \
    PostUserImpression, PostUserEngagement, RelatedPost, \
    check_seo_data_exists
from catalog.general.models import convert_price, Country, Region, City, JobFunction, SeniorityLabel, JobType, Language
from catalog.general.serializers import CountrySerializer, RegionSerializer, CitySerializer, JobFunctionSerializer, \
    SeniorityLabelSerializer, JobTypeSerializer
from catalog.category.models import Category
from catalog.category.serializers import CategorySerializer
from catalog.company.models import CompanyIndustry, CompanySize, CompanyType
from catalog.company.serializers import CompanyIndustrySerializer, CompanySizeSerializer, CompanyTypeSerializer
from catalog.product.models import ProductGroup
from catalog.product.serializers import ProductGroupSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from bs4 import BeautifulSoup
from catalog.file.models import get_external_image_url
import requests
from urllib.parse import urlparse
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .permissions import IsOwnerOrCompanyAdmin, IsOwner, IsPostOwnerOrCompanyAdmin, CanDeletePost, CanDeletePostObject, \
    IsPostOwnerOrCompanyAdminStrict
from catalog.company.permissions import IsOwnerOrCompanyAdmin as IsCompanyAdmin
from catalog.company.models import Company
from stream_django.enrich import Enrich
from stream_django.feed_manager import feed_manager
from catalog.user_profile.serializers import UserWithProfileMiddleSerializer
from catalog.user_profile.models import UserProfile
from catalog.hashtag.serializers import TagSerializer
from .documents import PostDocument
from elasticsearch_dsl import Q as Qel
from rest_framework import status
from hvad.utils import get_translation_aware_manager
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.utils import translation
from catalog.utils.utils import unique_slugify
from django.conf import settings
from datetime import datetime
from django.db import IntegrityError

import json


class DeletePostView(APIView):
    permission_classes = (IsAuthenticated, CanDeletePost)

    def delete(self, request, pk):
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(self.request, post)

        post.smart_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


def get_post_type_feed_id(type):
    obj = PostType.objects.get(pk=type)
    return str(obj.feed_id)


class UsersPostsByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostSerializer

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):

        user = self.request.user
        page = int(self.kwargs['page'])

        if page == 0:
            posts = Post.objects.filter(user=user, published=True, deleted=False)[:5]
        else:

            item_from = page * 5
            item_to = page * 5 + 5
            posts = Post.objects.filter(user=user, published=True, deleted=False)[item_from:item_to]
        return posts


class PostsForUserByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostSerializer

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):
        # user = self.request.user //TODO We should develop an algorithm to show relevant content for a user
        page = int(self.kwargs['page'])

        if page == 0:
            posts = Post.objects.filter(published=True, deleted=False)[:5]
        else:

            item_from = page * 5
            item_to = page * 5 + 5
            posts = Post.objects.filter(published=True, deleted=False)[item_from:item_to]
        return posts


user_actor_verbs = [
    'company_follower',
    'profile_follower',
    'like',
    'comment',
    'comment_like'

]

comment_verbs = [
    'comment', 'comment_like'
]


class UserFeedView(APIView):
    permission_classes = (IsAuthenticated,)

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return super(UserFeedView, self).dispatch(*args, **kwargs)

    @staticmethod
    def get_serialized_object_or_none(obj, context):

        if hasattr(obj, 'activity_object_serializer_class'):
            obj = obj.activity_object_serializer_class(obj, context=context).data

        else:
            obj = None  # Could also raise exception here
        return obj

    @staticmethod
    def get_default_serialized_object_or_none(obj, context):

        if hasattr(obj, 'activity_object_serializer_class'):
            obj = obj.activity_object_serializer_class(obj, context=context, language='en').data

        else:
            obj = None  # Could also raise exception here
        return obj

    def get_activity_serializer(self, data, serializer, **kwargs):

        current_currency = self.request.GET.get('current_currency', 1)

        context = {'request': self.request,
                   'current_currency': current_currency}

        return serializer(data, context=context, **kwargs)

    def serialize_activities(self, activities):
        current_currency = self.request.GET.get('current_currency', 1)
        for item in activities:
            i = 0
            for activity in item['activities']:
                if activity['verb'] in user_actor_verbs:
                    activity['actor'] = UserWithProfileMiddleSerializer(activity['actor'],
                                                                        context={'request': self.request}).data
                else:
                    activity['actor'] = None

                if i == 0:
                    if item['verb'] == 'post' or item['verb'] == 'comment' or item['verb'] == 'comment_like':

                        activity['object'] = self.get_serialized_object_or_none(activity['object'],
                                                                                context={'request': self.request,
                                                                                         'current_currency': current_currency})

                        activity['target'] = None
                    else:

                        if item['verb'] == 'tagged':
                            activity['object'] = TagSerializer(activity['object'],
                                                               context={'request': self.request}).data
                        else:

                            obj = self.get_serialized_object_or_none(activity['object'],
                                                                     context={'request': self.request,
                                                                              'current_currency': current_currency})

                            activity['object'] = obj

                        if item['verb'] == 'company_follower' or item['verb'] == 'followcompany':
                            target = self.get_serialized_object_or_none(activity['target'],
                                                                        context={'request': self.request,
                                                                                 'current_currency': current_currency})
                            if not target['name']:
                                target = self.get_default_serialized_object_or_none(activity['target'],
                                                                                    context={
                                                                                        'request': self.request,
                                                                                        'current_currency': current_currency})

                            activity['target'] = target
                        else:
                            activity['target'] = self.get_serialized_object_or_none(activity['target'],
                                                                                    context={'request': self.request,
                                                                                             'current_currency': current_currency})
                else:
                    activity['target'] = None
                    activity['object'] = None

                i = i + 1

        return activities

    def get(self, request, page):

        type = self.request.GET.get('type', None)

        feed_name = 'timeline_aggregated'
        if type:
            feed_id = get_post_type_feed_id(type)
            feed_name = feed_name + feed_id

        enricher = Enrich(fields=['actor', 'object', 'target'])

        feed = feed_manager.get_feed(feed_name, request.user.id)
        if page == 0:
            activities = feed.get(limit=5, mark_seen='all')['results']
        else:
            item_from = int(page) * 5

            activities = feed.get(limit=5, offset=item_from, mark_seen='all')['results']

        # enriched_activities = enricher.enrich_activities(posts)
        # print(enriched_activities)

        posts = []
        user_activities = []
        company_activities = []
        filters = []
        tagged_activities = []
        comment_activities = []
        for activity in activities:
            if activity['verb'] == 'post':
                posts.append(activity)
            if activity['verb'] == 'filter':
                filters.append(activity)
            if activity['verb'] in comment_verbs:
                comment_activities.append(activity)
            if activity['verb'] == 'like':
                user_activities.append(activity)
            if activity['verb'] == 'tagged':
                tagged_activities.append(activity)

            if activity['verb'] == 'company_follower' or activity['verb'] == 'followcompany':
                company_activities.append(activity)

        enriched_activities = enricher.enrich_aggregated_activities(posts)

        serialized_activities = self.get_activity_serializer(enriched_activities, AggregatedPostsSerializer,
                                                             many=True)

        data = serialized_activities.data

        enriched_activities = enricher.enrich_aggregated_activities(comment_activities)

        serialized_activities = self.get_activity_serializer(enriched_activities, AggregatedPostsCommentsSerializer,
                                                             many=True)

        data = data + serialized_activities.data

        enriched_activities = enricher.enrich_aggregated_activities(user_activities)

        serialized_activities = self.get_activity_serializer(enriched_activities, AggregatedPostsActivitiesSerializer,
                                                             many=True)

        data = data + serialized_activities.data

        enriched_activities = enricher.enrich_aggregated_activities(company_activities)

        serialized_activities = self.get_activity_serializer(enriched_activities, AggregatedCompanysSerializer,
                                                             many=True)

        data = data + serialized_activities.data

        enriched_activities = enricher.enrich_aggregated_activities(filters)

        serialized_activities = self.get_activity_serializer(enriched_activities, AggregatedFilterPostsSerializer,
                                                             many=True)

        data = data + serialized_activities.data

        enriched_activities = enricher.enrich_aggregated_activities(tagged_activities)

        serialized_activities = self.get_activity_serializer(enriched_activities, AggregatedTagedPostsSerializer,
                                                             many=True)
        data = data + serialized_activities.data

        return Response(data)


class FilteredPostsByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostSerializer

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return super(FilteredPostsByPageView, self).dispatch(*args, **kwargs)

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):
        page = int(self.kwargs['page'])
        user = self.request.GET.get('user', None)
        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        company = self.request.GET.get('company', None)
        product = self.request.GET.get('product', None)
        community = self.request.GET.get('community', None)
        related_user = self.request.GET.get('related_user', None)
        related_company = self.request.GET.get('related_company', None)
        related_product = self.request.GET.get('related_product', None)
        type = self.request.GET.get('type', None)
        tag = self.request.GET.get('tag', None)
        search_word = self.request.GET.get('search_word', None)
        attributes = self.request.GET.get('attributes', None)
        currency = self.request.GET.get('currency', None)
        pricefrom = self.request.GET.get('pricefrom', None)
        priceto = self.request.GET.get('priceto', None)
        post_status = self.request.GET.get('published', None)

        job_type = self.request.GET.get('job_type', None)
        job_function = self.request.GET.get('job_function', None)
        seniority_label = self.request.GET.get('seniority_label', None)

        # if search_word is not None:
        #
        #     s = PostDocument.search()
        #     filter_list = Qel("multi_match", query=search_word, fields=['comment',
        #                                                                 'city_name',
        #                                                                 'title',
        #                                                                 'post_title',
        #                                                                 'description',
        #                                                                 'category', 'community', 'product', 'company',
        #                                                                 'user'
        #
        #                                                                 ])
        #     filter_list = filter_list & Qel('match', published=True)
        #     filter_list = filter_list & Qel('match', is_open_community=True)
        #     filter_list = filter_list & Qel('match', deleted=False)
        #
        #     if type is not None:
        #         filter_list = filter_list & Qel('match', type=type)
        #     if country is not None:
        #         filter_list = filter_list & Qel('match', country=country)
        #     if city is not None:
        #         filter_list = filter_list & Qel('match', city=city)
        #     if region is not None:
        #         filter_list = filter_list & Qel('match', region=region)
        #     if category is not None:
        #         filter_list = filter_list & Qel('match', post_categories=category)
        #     if job_type is not None:
        #         filter_list = filter_list & Qel('match', job_type=job_type)
        #     if job_function is not None:
        #         filter_list = filter_list & Qel('match', job_function=job_function)
        #     if seniority_label is not None:
        #         filter_list = filter_list & Qel('match', seniority=seniority_label)
        #
        #         # filter_list = filter_list & Qel('match', post_categories__category=category)
        #
        #     s = s.query(filter_list).sort('-promotion','-promotion_grade')
        #
        #     if page == 0:
        #         s = s[:5]
        #     else:
        #         item_from = page * 5
        #         item_to = page * 5 + 5
        #         s = s[item_from:item_to]
        #
        #     response = s.execute()
        #
        #     response_dict = response.to_dict()
        #     hits = reversed(response_dict['hits']['hits'])
        #
        #     ids = [hit['_source']['id'] for hit in hits]
        #     posts = Post.objects.filter(id__in=ids).order_by('-promotion','-promotion_grade', '-id')
        #
        # else:

        filter_list = Q(deleted=False)

        if not user and not company:
            filter_list = filter_list & Q(prohibited=False)

        show_posts_without_category = False
        if user is not None:
            filter_list = filter_list & Q(user=user, company=None)
            show_posts_without_category = True
        if company is not None:
            filter_list = filter_list & Q(company=company)
            show_posts_without_category = True
        if product is not None:
            filter_list = filter_list & Q(product=product)
            show_posts_without_category = True
        if community is not None:
            filter_list = filter_list & Q(community=community)
            show_posts_without_category = True

        if related_company is not None:
            filter_list = filter_list & Q(related_company=related_company)
            show_posts_without_category = True
        if related_user is not None:
            filter_list = filter_list & Q(related_user=related_user)
            show_posts_without_category = True
        if related_product is not None:
            filter_list = filter_list & Q(related_product=related_product)
            show_posts_without_category = True

        if type is not None:
            filter_list = filter_list & Q(type=type)
        if job_type is not None:
            filter_list = filter_list & Q(post_job__job_type=job_type)
            show_posts_without_category = True

        if job_function is not None:
            filter_list = filter_list & Q(post_job__job_function=job_function)
            show_posts_without_category = True
        if seniority_label is not None:
            filter_list = filter_list & Q(post_job__seniority=seniority_label)
            show_posts_without_category = True

        if category is not None:
            filter_list = filter_list & Q(post_categories__category=category)
        if country is not None:
            filter_list = filter_list & Q(country=country)
        if city is not None:
            filter_list = filter_list & Q(city=city)
        if region is not None:
            filter_list = filter_list & Q(city__region=region)

        if post_status == 'true':
            filter_list = filter_list & Q(published=True)

        if tag is not None:
            tag = tag.lower()
            filter_list = filter_list & Q(tags__name__iexact=tag)
            show_posts_without_category = True

        if not show_posts_without_category:
            filter_list = filter_list & Q(category__isnull=False)

        if currency is not None:
            if pricefrom is not None:
                price = convert_price(int(pricefrom), int(currency), 1)
                filter_list = filter_list & Q(post_offering__price_usd__gte=price)

            if priceto is not None:
                price = convert_price(int(priceto), int(currency), 1)
                filter_list = filter_list & Q(post_offering__price_usd__lte=price)

        if (community is None):
            filter_list = filter_list & Q(community__isnull=True)

        if search_word is not None:
            filter_list = filter_list & (Q(title__icontains=search_word) | Q(post_title__icontains=search_word)
                                         | Q(description__icontains=search_word) | Q(comment__icontains=search_word))

        posts = Post.objects.filter(filter_list)

        if attributes is not None:
            attributes = json.loads(attributes)
            for attribute in attributes:
                type = attribute.get('type')
                multiple = attribute.get('multiple')

                id = attribute.get('attribute')
                if type == 1 and multiple == False:
                    value_list = attribute.get('value_list')
                    posts = posts.filter(attributes__attribute=id, attributes__values__value_list=value_list)

                if type == 1 and multiple == True:
                    multiple_values = attribute.get('values')
                    for value in multiple_values:
                        posts = posts.filter(attributes__attribute=id, attributes__values__value_list=value)

                if type == 4:
                    posts = posts.filter(attributes__attribute=id, attributes__values__value_boolean=True)

                if type == 2 or type == 5:
                    min_max_values = attribute.get('values')
                    if type == 2:
                        posts = posts.filter(attributes__attribute=id,
                                             attributes__values__value_number__gte=min_max_values[0],
                                             attributes__values__value_number__lte=min_max_values[1])
                    if type == 5:
                        posts = posts.filter(attributes__attribute=id,
                                             attributes__values__value_integer__gte=min_max_values[0],
                                             attributes__values__value_integer__lte=min_max_values[1])

        ordering = ['-promotion', '-promotion_grade', '-id']
        if page == 0:
            posts = posts.order_by(*ordering)[:5]
        else:
            item_from = page * 5
            item_to = page * 5 + 5
            posts = posts.order_by(*ordering)[item_from:item_to]

        return posts


class PostDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = (AllowAny, IsOwnerOrCompanyAdmin)
    serializer_class = PostSerializer
    queryset = Post.objects.filter(deleted=False)

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}


class CreatePostView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}


class UrlPreviewView(APIView):
    permission_classes = (AllowAny,)

    def put(self, request):
        res = get_url_metta_info(request.data['url'])

        return res


def get_url_metta_info(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }
    url = url.strip()
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.content, 'html.parser')

    if soup.title:
        title = soup.title.string
    else:
        title = None

    desc = soup.find(attrs={"name": "description"})

    if desc:
        desc = desc['content'].strip()
    else:
        desc = None

    og_image = soup.find(attrs={"property": "og:image"})

    if og_image:
        og_image = og_image['content'].strip()
    else:
        og_image = soup.find(attrs={"property": "og:image:secure_url"})

        if og_image:
            og_image = og_image['content'].strip()
        else:
            image = None

            for pic in soup.find_all('img'):
                src = pic.get('src')
                if src:
                    if 'http' in src:
                        image = src
                        break

            if image:
                og_image = image

            else:
                og_image = None

    image = og_image
    if og_image:
        if 'https' not in og_image:
            image = get_external_image_url(url, og_image)

    parsed_uri = urlparse(url)
    site_name = '{uri.netloc}'.format(uri=parsed_uri)
    if site_name.startswith('www.'):
        site_name = site_name[4:]

    if not title:
        title = site_name
    data = {
        'title': title,
        'description': desc,
        'image': image,
        'site_name': site_name
    }

    return Response(data)


class PostCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = PostCategorySerializer

    def get_queryset(self):
        post = self.kwargs['post']

        return PostCategory.objects.filter(post=post, post_category=True)


class PostTypesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostTypeSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(PostTypesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        object_related = self.request.GET.get('object_related', None)
        exclude_article = self.request.GET.get('exclude_article', None)
        language_code = self.request.GET.get('language_code', None)
        filter_list = Q()

        if object_related:
            if object_related == 'True':
                filter_list = Q(object_related=True)
            if object_related == 'False':
                filter_list = Q(object_related=False)

        if language_code:
            objects = PostType.objects.language(language_code).filter(filter_list).order_by('position')
        else:
            objects = PostType.objects.language().filter(filter_list).order_by('position')

        if exclude_article:
            objects = objects.exclude(code='article')

        return objects


class CreatePostCommentView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer


class DeletePostCommentView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, CanDeletePostObject)
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer


class UpdatePostCommentView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer


class PostCommentsByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostCommentSerializer

    def get_queryset(self):
        parent = int(self.kwargs['parent'])
        post = int(self.kwargs['post'])
        page = int(self.kwargs['page'])

        if parent == 0:
            comments = PostComment.objects.filter(post=post, parent__isnull=True, user__is_active=True)
        else:
            comments = PostComment.objects.filter(post=post, parent=parent, user__is_active=True)

        if page == 0:
            comments = comments.order_by('id')[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            comments = comments.order_by('id')[item_from:item_to]
        return comments


class CreatePostLikeView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer


class DeletePostLikeView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = PostLikeSerializer

    def get_object(self):
        user = self.request.user
        post = self.kwargs['post']
        obj = PostLike.objects.get(user=user, post=post)
        return obj


class CreatePostCommentLikeView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = PostCommentLike.objects.all()
    serializer_class = PostCommentLikeSerializer


class DeletePostCommentLikeView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = PostCommentLikeSerializer

    def get_object(self):
        user = self.request.user
        comment = self.kwargs['comment']
        obj = PostCommentLike.objects.get(user=user, comment=comment)
        return obj


class PostLikesByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostLikeSerializer

    def get_queryset(self):

        post = self.request.GET.get('post', None)
        page = int(self.kwargs['page'])

        likes = PostLike.objects.filter(post=post, user__is_active=True)

        if page == 0:
            likes = likes.order_by('-id')[:30]
        else:
            item_from = page * 30
            item_to = page * 30 + 30
            likes = likes.order_by('-id')[item_from:item_to]
        return likes


class LikesCountView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        post = self.request.GET.get('post', None)
        comment = self.request.GET.get('comment', None)

        count = 0

        if post:
            count = PostLike.objects.filter(post=post, user__is_active=True).count()
        if comment:
            count = PostCommentLike.objects.filter(comment=comment, user__is_active=True).count()

        data = {'count': count}

        return Response(data)


class ChangePostStatusView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)

    def put(self, request, post, published):

        if published == 'false':
            post_status = False
        else:
            post_status = True

        try:
            post_object = Post.objects.get(pk=post)
            self.check_object_permissions(self.request, post_object)
            post_object.published = post_status
            if (post_status):
                post_object.create_feed(True)
            else:
                post_object.delete_all_feed()

            post_object.save()
            return Response({'res': True})
        except Post.DoesNotExist:
            return status.HTTP_404_NOT_FOUND


class PostCommentLikesByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostCommentLikeSerializer

    def get_queryset(self):

        comment = self.request.GET.get('comment', None)
        page = int(self.kwargs['page'])

        likes = PostCommentLike.objects.filter(comment=comment, user__is_active=True)

        if page == 0:
            likes = likes.order_by('-id')[:30]
        else:
            item_from = page * 30
            item_to = page * 30 + 30
            likes = likes.order_by('-id')[item_from:item_to]
        return likes


class PostView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostPreviewSerializer

    def get_object(self):
        pk = self.kwargs['pk']
        try:
            post = Post.objects.get(deleted=False, id=pk)
            check_related_posts(post)
            return post
        except Post.DoesNotExist:
            return status.HTTP_404_NOT_FOUND


class PostBySlugView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostPreviewSerializer

    def get_object(self):

        slug = self.kwargs['slug']
        sslug = self.kwargs['sslug']
        subject = self.kwargs['subject']

        if subject == 'c':
            company = Company.objects.untranslated().get(slug=sslug)
            post = Post.objects.get(company=company, slug__iexact=slug, published=True)
        else:
            profile = UserProfile.objects.untranslated().get(slug=sslug)
            post = Post.objects.get(user=profile.user, slug__iexact=slug, published=True)
        check_related_posts(post)
        return post


class ApplicantStatusListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ApplicantStatusSerializer

    def get_queryset(self):
        queryset = ApplicantStatus.objects.language().order_by('position')
        return queryset


class PostApplicantsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = ApplicantSerializer

    def get_serializer_context(self):
        post_id = self.kwargs['post']

        post = Post.objects.get(pk=post_id)

        company = post.company_id
        return {'request': self.request, 'company': company}

    def get_queryset(self):
        post_id = self.kwargs['post']
        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        applicant_status = self.request.GET.get('applicant_status', None)
        job_type = self.request.GET.get('job_type', None)
        job_function = self.request.GET.get('job_function', None)
        seniority_label = self.request.GET.get('seniority_label', None)

        keyword = self.request.GET.get('keyword', None)

        post = Post.objects.get(pk=post_id)
        self.check_object_permissions(self.request, post)
        filter_list = Q(post=post_id)

        if country is not None:
            filter_list = filter_list & Q(user__user_profile__country=country)
        if city is not None:
            filter_list = filter_list & Q(user__user_profile__city=city)
        if region is not None:
            filter_list = filter_list & Q(user__user_profile__city__region=region)
        if applicant_status is not None:
            filter_list = filter_list & Q(status=applicant_status)
        if job_type is not None:
            filter_list = filter_list & Q(post__post_job__job_type=job_type)

        if job_function is not None:
            filter_list = filter_list & Q(post__post_job__job_function=job_function)
        if seniority_label is not None:
            filter_list = filter_list & Q(post__post_job__seniority=seniority_label)

        # objects = Applicant.objects.filter(filter_list)

        if keyword is not None:
            filter_list = filter_list & Q(Q(user__user_profile__first_name__icontains=keyword) |
                                          Q(user__user_profile__last_name__icontains=keyword))

        tr_manager = get_translation_aware_manager(Applicant)
        objects = tr_manager.language().filter(filter_list)
        if not objects:
            objects = tr_manager.language('en').filter(filter_list)

        if page == 0:
            objects = objects.order_by(order)[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects.order_by(order)[item_from:item_to]

        return objects


class UserApplicantsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicantSerializer

    def get_serializer_context(self):

        return {'request': self.request, 'company': None}

    def get_queryset(self):

        user_type = self.kwargs['user_type']
        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        applicant_status = self.request.GET.get('applicant_status', None)
        job_type = self.request.GET.get('job_type', None)
        job_function = self.request.GET.get('job_function', None)
        seniority_label = self.request.GET.get('seniority_label', None)

        keyword = self.request.GET.get('keyword', None)

        if user_type == "owner":
            filter_list = Q(post__user=self.request.user)
        else:
            filter_list = Q(user=self.request.user)
        # filter_list = filter_list & Q(post__company__isnull=True)

        if country is not None:
            filter_list = filter_list & Q(user__user_profile__country=country)
        if city is not None:
            filter_list = filter_list & Q(user__user_profile__city=city)
        if region is not None:
            filter_list = filter_list & Q(user__user_profile__city__region=region)
        if applicant_status is not None:
            filter_list = filter_list & Q(status=applicant_status)
        if job_type is not None:
            filter_list = filter_list & Q(post__post_job__job_type=job_type)

        if job_function is not None:
            filter_list = filter_list & Q(post__post_job__job_function=job_function)
        if seniority_label is not None:
            filter_list = filter_list & Q(post__post_job__seniority=seniority_label)

        # objects = Applicant.objects.filter(filter_list)

        if keyword is not None:

            if user_type == "owner":
                applicants = Applicant.objects.filter(filter_list, post__company__isnull=True)
                filter_list = filter_list & Q(pk__in=applicants)
            filter_list = filter_list & Q(Q(user__user_profile__first_name__icontains=keyword) |
                                          Q(user__user_profile__last_name__icontains=keyword))

            tr_manager = get_translation_aware_manager(Applicant)

            objects = tr_manager.language().filter(filter_list)

            if not objects:
                objects = tr_manager.language('en').filter(filter_list)


        else:
            if user_type == "owner":
                filter_list = filter_list & Q(post__company__isnull=True)

            objects = Applicant.objects.filter(filter_list)

        if page == 0:
            objects = objects.order_by(order)[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects.order_by(order)[item_from:item_to]

        return objects


class CompanyApplicantsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsCompanyAdmin)
    serializer_class = ApplicantSerializer

    def get_serializer_context(self):
        company = self.kwargs['company']
        return {'request': self.request, 'company': company}

    def get_queryset(self):

        company = self.kwargs['company']

        obj = Company.objects.get(id=company)
        self.check_object_permissions(self.request, obj)

        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        applicant_status = self.request.GET.get('applicant_status', None)
        job_type = self.request.GET.get('job_type', None)
        job_function = self.request.GET.get('job_function', None)
        seniority_label = self.request.GET.get('seniority_label', None)
        keyword = self.request.GET.get('keyword', None)

        filter_list = Q(post__company=company)

        if country is not None:
            filter_list = filter_list & Q(user__user_profile__country=country)
        if city is not None:
            filter_list = filter_list & Q(user__user_profile__city=city)
        if region is not None:
            filter_list = filter_list & Q(user__user_profile__city__region=region)
        if applicant_status is not None:
            filter_list = filter_list & Q(status=applicant_status)
        if job_type is not None:
            filter_list = filter_list & Q(post__post_job__job_type=job_type)

        if job_function is not None:
            filter_list = filter_list & Q(post__post_job__job_function=job_function)
        if seniority_label is not None:
            filter_list = filter_list & Q(post__post_job__seniority=seniority_label)

        # objects = Applicant.objects.filter(filter_list)

        if keyword is not None:
            filter_list = filter_list & Q(Q(user__user_profile__first_name__icontains=keyword) |
                                          Q(user__user_profile__last_name__icontains=keyword))

        tr_manager = get_translation_aware_manager(Applicant)
        objects = tr_manager.language().filter(filter_list)

        if not objects:
            objects = tr_manager.language('en').filter(filter_list)

        if page == 0:
            objects = objects.order_by(order)[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects.order_by(order)[item_from:item_to]

        return objects


class UpdateApplicantView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    queryset = Applicant.objects.all()
    serializer_class = ApplicantSerializer

    def get_serializer_context(self):
        post_id = self.request.data['post']

        post = Post.objects.get(pk=post_id)

        company = post.company_id
        return {'request': self.request, 'company': company}


class CreateApplicationView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ApplicantSerializer
    queryset = Applicant.objects.all()

    def get_serializer_context(self):
        return {'request': self.request, 'company': None}


class SetApplicantRatingView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    serializer_class = ApplicantSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        applicant = self.kwargs['applicant']

        try:
            obj = Applicant.objects.get(id=applicant)
        except Applicant.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.rating = value
        obj.reviewed = True
        obj.save()

        return Response({'value': value})


class UpdateApplicantCommentView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    serializer_class = ApplicantSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        applicant = self.kwargs['applicant']

        try:
            obj = Applicant.objects.get(id=applicant)
        except Applicant.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.comment = value
        obj.reviewed = True
        obj.save()

        return Response({'value': value})


class UpdateApplicantStatusView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    serializer_class = ApplicantSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        applicant = self.kwargs['applicant']

        try:
            obj = Applicant.objects.get(id=applicant)
        except Applicant.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.status_id = value
        obj.reviewed = True
        obj.save()

        return Response({'value': value})


class PostRespondStatusListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostRespondStatusSerializer

    def get_queryset(self):
        queryset = PostRespondStatus.objects.language().order_by('position')
        return queryset


class CreatePostRespondView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostRespondSerializer
    queryset = PostRespond.objects.all()

    def get_serializer_context(self):
        company = None
        if self.request.data['company']:
            company = self.request.data['company']

        return {'request': self.request, 'company': company}


class PostRespondsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = PostRespondSerializer

    def get_serializer_context(self):
        post_id = self.kwargs['post']
        post = Post.objects.get(pk=post_id)
        company = post.company_id
        return {'request': self.request, 'company': company}

    def get_queryset(self):
        post_id = self.kwargs['post']
        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        respond_status = self.request.GET.get('respond_status', None)

        keyword = self.request.GET.get('keyword', None)

        post = Post.objects.get(pk=post_id)
        self.check_object_permissions(self.request, post)
        filter_list = Q(post=post_id)

        if country is not None:
            filter_list = filter_list & Q(user__user_profile__country=country)
        if city is not None:
            filter_list = filter_list & Q(user__user_profile__city=city)
        if region is not None:
            filter_list = filter_list & Q(user__user_profile__city__region=region)
        if respond_status is not None:
            filter_list = filter_list & Q(status=respond_status)

        if keyword is not None:
            filter_list = filter_list & Q(Q(user__user_profile__first_name__icontains=keyword) |
                                          Q(user__user_profile__last_name__icontains=keyword) |
                                          Q(company__name__icontains=keyword) |
                                          Q(cover_letter=keyword))

        tr_manager = get_translation_aware_manager(PostRespond)
        objects = tr_manager.language().filter(filter_list)
        if not objects:
            objects = tr_manager.language('en').filter(filter_list)

        if page == 0:
            objects = objects.order_by(order)[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects.order_by(order)[item_from:item_to]

        return objects


class CompanyRespondsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsCompanyAdmin)
    serializer_class = PostRespondSerializer

    def get_serializer_context(self):
        company = self.kwargs['company']

        return {'request': self.request, 'company': company}

    def get_queryset(self):

        type_code = self.kwargs['type']
        user_type = self.kwargs['user_type']
        company = self.kwargs['company']
        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        respond_status = self.request.GET.get('respond_status', None)

        keyword = self.request.GET.get('keyword', None)

        obj = Company.objects.get(pk=company)
        self.check_object_permissions(self.request, obj)

        if user_type == 'owner':
            filter_list = Q(post__company=company, post__type__code=type_code)
        else:
            filter_list = Q(company=company, post__type__code=type_code)

        if country is not None:
            filter_list = filter_list & Q(user__user_profile__country=country)
        if city is not None:
            filter_list = filter_list & Q(user__user_profile__city=city)
        if region is not None:
            filter_list = filter_list & Q(user__user_profile__city__region=region)
        if respond_status is not None:
            filter_list = filter_list & Q(status=respond_status)

        if keyword is not None:
            filter_list = filter_list & Q(Q(user__user_profile__first_name__icontains=keyword) |
                                          Q(user__user_profile__last_name__icontains=keyword) |

                                          Q(cover_letter=keyword))

        tr_manager = get_translation_aware_manager(PostRespond)
        objects = tr_manager.language().filter(filter_list)
        if not objects:
            objects = tr_manager.language('en').filter(filter_list)

        if page == 0:
            objects = objects.order_by(order)[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects.order_by(order)[item_from:item_to]

        return objects


class UserRespondsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostRespondSerializer

    def get_serializer_context(self):

        return {'request': self.request, 'company': None}

    def get_queryset(self):
        user_type = self.kwargs['user_type']
        type_code = self.kwargs['type']
        page = int(self.kwargs['page'])
        order = self.kwargs['order']
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        respond_status = self.request.GET.get('respond_status', None)

        keyword = self.request.GET.get('keyword', None)
        if user_type == 'owner':
            filter_list = Q(post__user=self.request.user, post__type__code=type_code)
        else:
            filter_list = Q(user=self.request.user, company__isnull=True, post__type__code=type_code)

        if country is not None:
            filter_list = filter_list & Q(user__user_profile__country=country)
        if city is not None:
            filter_list = filter_list & Q(user__user_profile__city=city)
        if region is not None:
            filter_list = filter_list & Q(user__user_profile__city__region=region)
        if respond_status is not None:
            filter_list = filter_list & Q(status=respond_status)

        if keyword is not None:
            if user_type == 'owner':
                responds = PostRespond.objects.filter(filter_list, post__company__isnull=True)
                filter_list = filter_list & Q(pk__in=responds)

            filter_list = filter_list & Q(Q(user__user_profile__first_name__icontains=keyword) |
                                          Q(user__user_profile__last_name__icontains=keyword) |

                                          Q(cover_letter=keyword))

            tr_manager = get_translation_aware_manager(PostRespond)
            objects = tr_manager.language().filter(filter_list)

            if not objects:
                objects = tr_manager.language('en').filter(filter_list)

        else:
            if user_type == 'owner':
                objects = PostRespond.objects.filter(filter_list, post__company__isnull=True)
            else:
                objects = PostRespond.objects.filter(filter_list)

        if page == 0:
            objects = objects.order_by(order)[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects.order_by(order)[item_from:item_to]

        return objects


class SetPostRespondRatingView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    serializer_class = PostRespondSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        respond = self.kwargs['respond']

        try:
            obj = PostRespond.objects.get(id=respond)
        except PostRespond.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.rating = value
        obj.reviewed = True
        obj.save()

        return Response({'value': value})


class UpdatePostRespondCommentView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    serializer_class = PostRespondSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        respond = self.kwargs['respond']

        try:
            obj = PostRespond.objects.get(id=respond)
        except PostRespond.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.comment = value
        obj.reviewed = True
        obj.save()

        return Response({'value': value})


class UpdatePostRespondStatusView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)
    serializer_class = PostRespondSerializer

    def put(self, request, *args, **kwargs):
        value = request.data['value']
        respond = self.kwargs['respond']

        try:
            obj = PostRespond.objects.get(id=respond)
        except PostRespond.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.status_id = value
        obj.reviewed = True
        obj.save()

        return Response({'value': value, 'code': obj.status.code})


class CreateFavoritePostView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = FavoritePost.objects.all()
    serializer_class = FavoritePostSerializer

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}


class DeleteFavoritePostView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = FavoritePostSerializer

    def get_object(self):
        post = self.kwargs['post']

        obj = FavoritePost.objects.get(post=post, user=self.request.user)
        self.check_object_permissions(self.request, obj)

        return obj


class FavoritePostsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoritePostSerializer

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        type = self.request.GET.get('type', None)
        attributes = self.request.GET.get('attributes', None)
        currency = self.request.GET.get('currency', None)
        pricefrom = self.request.GET.get('pricefrom', None)
        priceto = self.request.GET.get('priceto', None)
        job_type = self.request.GET.get('job_type', None)
        job_function = self.request.GET.get('job_function', None)
        seniority_label = self.request.GET.get('seniority_label', None)

        filter_list = Q(user=self.request.user)
        filter_list = filter_list & Q(post__published=True)

        if country is not None:
            filter_list = filter_list & Q(post__country=country)
        if city is not None:
            filter_list = filter_list & Q(post__city=city)
        if region is not None:
            filter_list = filter_list & Q(post__city__region=region)
        if type is not None:
            filter_list = filter_list & Q(post__type=type)
        if category is not None:
            filter_list = filter_list & Q(post__post_categories__category=category)

        if job_type is not None:
            filter_list = filter_list & Q(post__post_job__job_type=job_type)

        if job_function is not None:
            filter_list = filter_list & Q(post__post_job__job_function=job_function)
        if seniority_label is not None:
            filter_list = filter_list & Q(post__post_job__seniority=seniority_label)

        if currency is not None:
            if pricefrom is not None:
                price = convert_price(int(pricefrom), int(currency), 1)
                filter_list = filter_list & Q(post__post_offering__price_usd__gte=price)

            if priceto is not None:
                price = convert_price(int(priceto), int(currency), 1)
                filter_list = filter_list & Q(post__post_offering__price_usd__lte=price)

        posts = FavoritePost.objects.filter(filter_list)

        if attributes is not None:
            attributes = json.loads(attributes)
            for attribute in attributes:
                type = attribute.get('type')
                multiple = attribute.get('multiple')

                id = attribute.get('attribute')
                if type == 1 and multiple == False:
                    value_list = attribute.get('value_list')
                    posts = posts.filter(post__attributes__attribute=id,
                                         post__attributes__values__value_list=value_list)

                if type == 1 and multiple == True:
                    multiple_values = attribute.get('values')
                    for value in multiple_values:
                        posts = posts.filter(post__attributes__attribute=id, post__attributes__values__value_list=value)

                if type == 4:
                    posts = posts.filter(post__attributes__attribute=id, post__attributes__values__value_boolean=True)

                if type == 2 or type == 5:
                    min_max_values = attribute.get('values')
                    if type == 2:
                        posts = posts.filter(post__attributes__attribute=id,
                                             post__attributes__values__value_number__gte=min_max_values[0],
                                             post__attributes__values__value_number__lte=min_max_values[1])
                    if type == 5:
                        posts = posts.filter(post__attributes__attribute=id,
                                             post__attributes__values__value_integer__gte=min_max_values[0],
                                             post__attributes__values__value_integer__lte=min_max_values[1])

        if page == 0:
            posts = posts.order_by('-id')[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            posts = posts.order_by('-id')[item_from:item_to]

        return posts


class CreatePostImpressionView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        post = request.data['post']
        impression = request.data['impression']
        view = request.data['view']
        timestamp = request.data.get('timestamp', None)

        if timestamp:
            if request.user.id:

                try:
                    PostUserImpression.objects.get_or_create(user=request.user, post_id=post, impression=impression,
                                                             view=view,
                                                             timestamp=timestamp)
                except:
                    pass
            else:
                try:
                    PostUserImpression.objects.get_or_create(user=None, post_id=post, impression=impression, view=view,
                                                             timestamp=timestamp)
                except:
                    pass

        return Response({'result': 1})


class CreatePostEngagementView(generics.CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):

        post = request.data['post']
        type = request.data['type']
        timestamp = request.data.get('timestamp', None)

        if timestamp:
            if request.user.id:
                PostUserEngagement.objects.get_or_create(user=request.user, post_id=post, type=type,
                                                         timestamp=timestamp)
            else:
                PostUserEngagement.objects.get_or_create(user=None, post_id=post, type=type, timestamp=timestamp)

        return Response({'result': 1})


class CreatePostOptionVoteView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        post = request.data['post']

        option = request.data['option']

        post_inst = Post.objects.get(id=post)
        if not post_inst.multi_selection:
            PostOptionVote.objects.filter(post=post, user=self.request.user).delete()

        obj = PostOptionVote(post_id=post, option_id=option, user=self.request.user)
        obj.save()

        serializer = PostOptionVoteSerializer(obj, context={'request': request})

        return Response(serializer.data)


class DeletePostOptionVoteView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = PostOptionVoteSerializer

    def get_object(self):
        user = self.request.user
        option = self.kwargs['option']
        post = self.kwargs['post']
        obj = PostOptionVote.objects.get(user=user, post=post, option=option)
        return obj


class PostOptionVotesByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostOptionVoteSerializer

    def get_queryset(self):

        post = self.request.GET.get('post', None)
        option = self.request.GET.get('option', None)
        page = int(self.kwargs['page'])

        votes = PostOptionVote.objects.filter(post=post, option=option)

        if page == 0:
            votes = votes.order_by('-id')[:30]
        else:
            item_from = page * 30
            item_to = page * 30 + 30
            votes = votes.order_by('-id')[item_from:item_to]
        return votes


class FormUniversalFilterView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request, query, language):
        universal_filter = {
            'post_type': None,
            'country': None,
            'region': None,
            'city': None,
            'category': None,
            'product_group': None,
            'company_industry': None,
            'company_type': None,
            'company_size': None,
            'job_type': None,
            'job_function': None,
            'seniority_label': None,
        }

        if not language:
            language = 'en'

        translation.activate(language)
        if query is not None:
            try:
                query = json.loads(query)
            except:
                return Response(universal_filter)

            country = query.get('country', None)
            if country:

                try:
                    obj = Country.objects.language(language).fallbacks('en').get(slug=country)

                    obj_ser = CountrySerializer(obj)
                    universal_filter['country'] = obj_ser.data

                except Country.DoesNotExist:
                    pass

            region = query.get('region', None)
            if region:
                try:
                    obj = Region.objects.language(language).fallbacks('en').get(slug=region)
                    obj_ser = RegionSerializer(obj)
                    universal_filter['region'] = obj_ser.data

                except Region.DoesNotExist:
                    pass

            city = query.get('city', None)
            if city:

                try:
                    obj = City.objects.language(language).fallbacks('en').get(slug=city)

                    obj_ser = CitySerializer(obj)
                    universal_filter['city'] = obj_ser.data
                except City.DoesNotExist:
                    pass

            category = query.get('category', None)
            if category:

                try:
                    obj = Category.objects.language(language).fallbacks('en').get(slug=category)

                    obj_ser = CategorySerializer(obj)
                    universal_filter['category'] = obj_ser.data

                except Category.DoesNotExist:
                    pass

            company_type = query.get('company_type', None)
            if company_type:
                try:
                    obj = CompanyType.objects.language(language).fallbacks('en').get(slug=company_type)
                    obj_ser = CompanyTypeSerializer(obj)
                    universal_filter['company_type'] = obj_ser.data

                except CompanyType.DoesNotExist:
                    pass

            company_size = query.get('company_size', None)
            if company_size:
                try:
                    obj = CompanySize.objects.language(language).fallbacks('en').get(slug=company_size)
                    obj_ser = CompanySizeSerializer(obj)
                    universal_filter['company_size'] = obj_ser.data

                except CompanySize.DoesNotExist:
                    pass
            company_industry = query.get('company_industry', None)
            if company_industry:
                try:
                    obj = CompanyIndustry.objects.language(language).fallbacks('en').get(slug=company_industry)
                    obj_ser = CompanyIndustrySerializer(obj)
                    universal_filter['company_industry'] = obj_ser.data

                except CompanyIndustry.DoesNotExist:
                    pass

            job_type = query.get('job_type', None)
            if job_type:

                try:
                    obj = JobType.objects.language(language).fallbacks('en').get(slug=job_type)

                    obj_ser = JobTypeSerializer(obj)
                    universal_filter['job_type'] = obj_ser.data

                except JobType.DoesNotExist:
                    pass

            job_function = query.get('job_function', None)
            if job_function:

                try:
                    obj = JobFunction.objects.language(language).fallbacks('en').get(slug=job_function)

                    obj_ser = JobFunctionSerializer(obj)
                    universal_filter['job_function'] = obj_ser.data

                except JobFunction.DoesNotExist:
                    pass

            seniority_label = query.get('seniority_label', None)
            if seniority_label:

                try:
                    obj = SeniorityLabel.objects.language(language).fallbacks('en').get(slug=seniority_label)

                    obj_ser = SeniorityLabelSerializer(obj)
                    universal_filter['seniority_label'] = obj_ser.data

                except SeniorityLabel.DoesNotExist:
                    pass

            post_type = query.get('post_type', None)
            if post_type:
                try:
                    obj = PostType.objects.language(language).fallbacks('en').get(code=post_type)

                    obj_ser = PostTypeSerializer(obj)
                    universal_filter['post_type'] = obj_ser.data

                except PostType.DoesNotExist:
                    pass

            product_group = query.get('product_group', None)
            if product_group:
                try:
                    obj = ProductGroup.objects.language(language).fallbacks('en').get(pk=int(product_group))
                    obj_ser = ProductGroupSerializer(obj)
                    universal_filter['product_group'] = obj_ser.data

                except ProductGroup.DoesNotExist:
                    pass

        return Response(universal_filter)


class FeedFilterView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, query):
        feed_filter = {
            'filter_id': None,
            'following_status': False,
            'following_id': None,
            'able_to_follow': False
        }

        able_to_follow = False
        if query is not None:
            try:
                query = json.loads(query)
            except:
                return Response(feed_filter)

            filter_list = Q()

            country = query.get('country', None)
            region = query.get('region', None)

            if country:
                able_to_follow = True

                filter_list = filter_list & Q(country=int(country))

            else:
                filter_list = filter_list & Q(country__isnull=True)

            city = query.get('city', None)
            if city:
                able_to_follow = True
                filter_list = filter_list & Q(city=int(city))

            else:
                filter_list = filter_list & Q(city__isnull=True)

            category = query.get('category', None)
            if category:
                able_to_follow = True
                filter_list = filter_list & Q(category=int(category))

            else:
                filter_list = filter_list & Q(category__isnull=True)

            job_type = query.get('job_type', None)
            if job_type:
                if category:
                    able_to_follow = False
                else:
                    able_to_follow = True
                filter_list = filter_list & Q(job_type=int(job_type))

            else:
                filter_list = filter_list & Q(job_type__isnull=True)

            job_function = query.get('job_function', None)
            if job_function:
                if category:
                    able_to_follow = False
                else:
                    able_to_follow = True
                filter_list = filter_list & Q(job_function=int(job_function))

            else:
                filter_list = filter_list & Q(job_function__isnull=True)

            seniority = query.get('seniority', None)
            if seniority:
                if category:
                    able_to_follow = False
                else:
                    able_to_follow = True
                filter_list = filter_list & Q(seniority=int(seniority))

            else:
                filter_list = filter_list & Q(seniority__isnull=True)

            if region and not city:
                able_to_follow = False

            if able_to_follow:
                try:
                    post_type_q = Q()
                    post_type = query.get('post_type', None)

                    if post_type:
                        post_type_q = post_type_q & Q(post_type=int(post_type))

                    else:
                        post_type_q = post_type_q & Q(post_type__isnull=True)

                    filter_obj = PostSEOData.objects.get(filter_list & post_type_q)
                    feed_filter['filter_id'] = filter_obj.id

                    if request.user.id:
                        feed_filter['able_to_follow'] = able_to_follow
                        try:
                            status = PostSEODataFollower.objects.get(filter=filter_obj.id, user=request.user.id)
                            feed_filter['following_status'] = True
                            feed_filter['following_id'] = status.id

                        except PostSEODataFollower.DoesNotExist:
                            feed_filter['following_status'] = False
                            feed_filter['following_id'] = None
                            if post_type:
                                try:
                                    filter_obj = PostSEOData.objects.get(filter_list & Q(post_type__isnull=True))
                                    try:
                                        status = PostSEODataFollower.objects.get(filter=filter_obj.id,
                                                                                 user=request.user.id)
                                        feed_filter['following_status'] = True
                                        feed_filter['following_id'] = status.id
                                        feed_filter['able_to_follow'] = False

                                    except PostSEODataFollower.DoesNotExist:
                                        pass


                                except PostSEODataFollower.DoesNotExist:
                                    pass


                    else:
                        feed_filter['able_to_follow'] = False


                except PostSEOData.DoesNotExist:
                    return Response(feed_filter)

        return Response(feed_filter)


class FollowFilterView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        feed_filter = {
            'filter_id': None,
            'following_status': False,
            'following_id': None,
            'able_to_follow': True
        }
        filter_id = request.data.get('filter_id', None)

        try:
            filter_obj = PostSEOData.objects.get(id=filter_id)
        except PostSEOData.DoesNotExist:
            return Response(feed_filter)

        follow_obj = PostSEODataFollower.objects.create(user=request.user, filter=filter_obj)

        if not filter_obj.post_type:
            types = PostType.objects.all()
            for type in types:
                follow_type_obj = check_seo_data_exists(filter_obj.category, type, filter_obj.country,
                                                        filter_obj.city,
                                                        filter_obj.seniority, filter_obj.job_function,
                                                        filter_obj.job_type)

                PostSEODataFollower.objects.get_or_create(user=request.user, filter_id=follow_type_obj)

        feed_filter['following_status'] = True
        feed_filter['filter_id'] = filter_id
        feed_filter['following_id'] = follow_obj.id

        return Response(feed_filter)


class DeleteFollowFilterView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user = self.request.user
        filter_id = self.kwargs['filter']
        obj = PostSEODataFollower.objects.get(user=user, filter=filter_id)
        if not obj.filter.post_type:
            types = PostType.objects.all()
            for type in types:
                follow_type_obj = check_seo_data_exists(obj.filter.category, type, obj.filter.country,
                                                        obj.filter.city,
                                                        obj.filter.seniority, obj.filter.job_function,
                                                        obj.filter.job_type)

                PostSEODataFollower.objects.filter(user=self.request.user, filter_id=follow_type_obj).delete()

        if obj.filter.post_type:
            follow_type_obj = check_seo_data_exists(obj.filter.category, None, obj.filter.country,
                                                    obj.filter.city,
                                                    obj.filter.seniority, obj.filter.job_function,
                                                    obj.filter.job_type)
            PostSEODataFollower.objects.filter(user=self.request.user, filter_id=follow_type_obj).delete()

        return obj


class CreateArticleView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        company = request.data.get('company', None)
        user = request.data.get('user', None)
        product = request.data.get('product', None)
        category = request.data.get('category', None)
        country = request.data.get('country', None)
        city = request.data.get('city', None)
        default_lang = request.data.get('default_lang', None)

        language = Language.objects.language('en').get(pk=default_lang)

        post = Post(type_id=settings.ARTICLES_TYPE_ID, user_id=user, company_id=company, product_id=product,
                    published=False)
        post.save()

        article = Article.objects.language(language.code).create(post=post, draft_category_id=category,
                                                                 draft_country_id=country, to_publish=False,
                                                                 draft_city_id=city, default_lang_id=default_lang)

        serializer = ArticleSerializer(article, context={'request': request})

        return Response(serializer.data)


class UpdateArticleView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdminStrict)

    serializer_class = ArticleSerializer

    def get_object(self):
        language = self.kwargs['language']
        post = self.kwargs['post']

        try:
            obj = Article.objects.language(language).get(post=post)
        except:
            obj = Article.objects.untranslated().get(post=post)
            langs = obj.get_available_languages()
            obj = Article.objects.language(langs[0]).get(post=post)

        self.check_object_permissions(self.request, obj)

        return obj


class ArticleBySlugView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ArticleSerializer

    def get_object(self):

        slug = self.kwargs['slug']
        sslug = self.kwargs['sslug']
        subject = self.kwargs['subject']

        if subject == 'c':
            company = Company.objects.untranslated().get(slug=sslug)
            post = Post.objects.get(company=company, slug__iexact=slug, published=True)
        else:
            profile = UserProfile.objects.untranslated().get(slug=sslug)
            post = Post.objects.get(user=profile.user, slug__iexact=slug, published=True)

        obj = Article.objects.language().fallbacks(post.article.default_lang.code).get(pk=post.id)
        check_related_posts(post)
        return obj


class PublishArticleView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdminStrict)

    def put(self, request, *args, **kwargs):

        post = request.data['post']
        default_lang = request.data['default_lang']

        if default_lang != settings.EN_LANG_ID:
            current_article = Article.objects.untranslated().get(pk=post)
            langs = current_article.get_available_languages()
            if 'en' in langs:
                current_article.default_lang_id = settings.EN_LANG_ID
                current_article.save()
                default_lang = settings.EN_LANG_ID

        lang = Language.objects.get(pk=default_lang)
        default_article = Article.objects.language(lang.code).get(pk=post)
        self.check_object_permissions(self.request, default_article)
        if default_article.title_draft:

            default_article.to_publish = False
            default_article.image = default_article.image_draft

            default_article.prepare_published_fields()

            if not default_article.post.slug and default_article.seo_title:
                if default_article.post.company:
                    queryset = Post.objects.filter(company=default_article.post.company)
                else:
                    queryset = Post.objects.filter(user=default_article.post.user)
                unique_slugify(default_article.post, default_article.seo_title, queryset=queryset)

            default_article.post.tags.set(*default_article.tags.all(), clear=False)

            # for tag in default_article.tags.all():
            #     tag_object = TaggedItem(content_object=default_article.post, tag=tag)
            #     tag_object.save()

            default_article.post.tags = default_article.tags
            default_article.post.title = default_article.title
            default_article.post.description = default_article.description
            if default_article.image_draft:
                default_article.post.image_url = default_article.image_draft.file_url
            else:
                default_article.post.image_url = None

            default_article.post.site_name = 'uafine.com'
            default_article.post.published = True
            default_article.post.category = default_article.draft_category
            default_article.post.country = default_article.draft_country
            default_article.post.city = default_article.draft_city
            default_article.post.save()
            langs = default_article.get_available_languages()

            for lang in langs:

                if lang != default_article.default_lang.code:
                    article = Article.objects.language(lang).get(post=post)

                    if article.title_draft and article.text_draft:
                        article.prepare_published_fields()

                    else:
                        article.delete_translation(lang)

            serializer = ArticleSerializer(default_article, context={'request': request})

            return Response(serializer.data)
        else:
            return status.HTTP_400_BAD_REQUEST


class DeleteArticleLanguageView(APIView):
    permission_classes = (IsAuthenticated, IsPostOwnerOrCompanyAdmin)

    def post(self, request, pk, language):

        article = Article.objects.language(language).get(pk=pk)
        self.check_object_permissions(self.request, article)

        article.delete_translation(language)
        article = Article.objects.untranslated().get(pk=pk)

        langs = article.get_available_languages()

        if article.default_lang not in langs:
            if 'en' in langs:
                default_lang = Language.objects.language('en').get(code='en')

            else:
                default_lang = Language.objects.language('en').get(code=langs[0])

            article.default_lang = default_lang
            article.save()

        article = Article.objects.language(article.default_lang.code).get(pk=pk)

        serializer = ArticleSerializer(article, context={'request': request})

        return Response(serializer.data)


def check_related_posts(post: Post):
    if not post.manual_related_posts:
        date1 = datetime.today().date()

        posts_status = True
        try:
            relate_post = RelatedPost.objects.filter(post=post).first()
            if relate_post:
                if relate_post.create_date.date() != date1:
                    posts_status = False
            else:
                posts_status = False


        except RelatedPost.DoesNotExist:
            posts_status = False

        if not posts_status:

            RelatedPost.objects.filter(post=post).delete()
            i = 0

            if post.company:
                filter_list_actor = Q(company=post.company)
            else:
                filter_list_actor = Q(user=post.user)

            if post.category:
                main_filter = Q(type=post.type, category=post.category)
                i = generate_related_posts_by_filter(i, post, main_filter, filter_list_actor)
                if i < 10:
                    main_filter = Q(category=post.category)
                    i = generate_related_posts_by_filter(i, post, main_filter, filter_list_actor)
                    if i < 10:
                        if post.category.parent:
                            main_filter = Q(type=post.type, category=post.category.parent)
                            i = generate_related_posts_by_filter(i, post, main_filter, filter_list_actor)
                            if i < 10:
                                main_filter = Q(category=post.category.parent)
                                i = generate_related_posts_by_filter(i, post, main_filter, filter_list_actor)

            if i < 10:
                main_filter = Q(type=post.type)
                generate_related_posts_by_filter(i, post, main_filter, filter_list_actor)


def generate_related_posts_by_filter(i, post, main_filter, filter_list_actor):
    general_filter = Q(deleted=False, published=True, is_video_url=False, shared_post__isnull=True,
                       post_language=post.post_language) & (Q(allow_index=True) | Q(type__code='article'))

    location_filter = Q()
    if post.country:
        location_filter = Q(country=post.country)
    if post.city:
        location_filter = location_filter & Q(city=post.city)

    filter_list = location_filter & main_filter & filter_list_actor & general_filter

    i = filter_and_create_related_posts(post, i, filter_list)

    if i < 10:
        filter_list = location_filter & main_filter & general_filter
        i = filter_and_create_related_posts(post, i, filter_list)
        if i < 10:
            if post.country and post.city:
                location_filter = Q(country=post.country)
                filter_list = location_filter & main_filter & filter_list_actor & general_filter
                i = filter_and_create_related_posts(post, i, filter_list)
                if i < 10:
                    filter_list = location_filter & main_filter & general_filter
                    i = filter_and_create_related_posts(post, i, filter_list)

        if i < 10:
            filter_list = filter_list_actor & main_filter & general_filter
            i = filter_and_create_related_posts(post, i, filter_list)

        if i < 10:
            filter_list = main_filter & general_filter
            i = filter_and_create_related_posts(post, i, filter_list)

    return i


def filter_and_create_related_posts(post, i, filter_query):
    created_posts = Post.objects.filter(main_posts__post=post)

    related_posts = Post.objects.filter(filter_query).exclude(id__in=created_posts).exclude(id=post.id).exclude(
        type__code='review').exclude(
        type__code='question').order_by('-promotion', '-promotion_grade', '-id')[:10 - i]

    for related_post in related_posts:

        try:
            RelatedPost.objects.create(post=post, related_post=related_post)
            i += 1
        except IntegrityError:
            pass
    return i
