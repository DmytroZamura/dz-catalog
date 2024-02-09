from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import UserProfileCategorySerializer, UserProfileSerializer, UserSettingsSerializer, \
    UserProfileShortSerializer, UserProfileCountryInterestSerializer, \
    UserProfileFollowerSerializer, ResumeSerializer
from rest_framework import generics
from .models import UserProfileCategory, UserProfile, UserProfileCountryInterest, UserProfileFollower, Resume
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser

from catalog.category.models import Category
from catalog.company.models import CompanyUser, Company
from catalog.community.models import Community
from catalog.product.models import Product
from taggit.models import Tag

from catalog.category.serializers import CategorySerializer
from .documents import ProfileDocument

from .permissions import IsOwnerOrReadOnly, IsOwnerDetails
from sorl.thumbnail import get_thumbnail
from django.db.models import Q
# from elasticsearch_dsl import Q as Qel

from django.shortcuts import get_object_or_404

from django.core.exceptions import ObjectDoesNotExist
import boto3
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


def get_ordering(code, parent_model=''):
    if parent_model == 'profile__':
        ordering = ['-create_date', '-id']
    else:
        ordering = ['-' + parent_model + 'update_date', '-' + parent_model + 'eventsqty__followers', '-id']

    if code == 'rating':
        ordering = ['-' + parent_model + 'eventsqty__rating', '-' + parent_model + 'eventsqty__related_reviews',
                    '-' + parent_model + 'eventsqty__followers', '-id']

    if code == 'popularity':
        ordering = ['-' + parent_model + 'eventsqty__followers',
                    '-' + parent_model + 'eventsqty__related_reviews', '-id']

    return ordering


def get_elastic_ordering(code, latitude=0, longitude=0):
    ordering = ['-update_date', '-followers']
    if code == 'rating':
        ordering = ['-rating', '-related_reviews', '-followers', '-update_date']
    if code == 'popularity':
        ordering = ['-followers', '-related_reviews', '-update_date']

    if code == 'close':
        ordering = [{'_geo_distance': {
            'location': {'lat': latitude, 'lon': longitude},
            "order": "asc",
            "unit": "km",
            "distance_type": "arc"
        }}, '-followers', '-rating', '-update_date']

    return ordering


class DeleteUserProfileView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)

    def delete(self, request, format=None):
        client = boto3.client('cognito-idp', region_name=settings.COGNITO_AWS_REGION)
        client.admin_delete_user(
            UserPoolId=settings.COGNITO_USER_POOL,
            Username=request.user.username
        )

        user = request.user

        user.user_profile.smart_delete()
        user.is_active = False
        user.first_name = ''
        user.last_name = ''
        user.username = 'd' + str(user.id)
        user.email = ''
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileImageUploadView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):

        file_obj = request.data['file']
        user_image = UserProfile.objects.language().fallbacks('en').get(user=request.user.pk)
        self.check_object_permissions(self.request, user_image)
        user_image.image = file_obj
        try:
            user_image.save()
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:

            serializer = UserProfileSerializer(user_image, context={'request': request})

            return Response(serializer.data)


class UserProfileDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    serializer_class = UserProfileSerializer

    def get_object(self):
        language = self.kwargs['language']

        obj = UserProfile.objects.language(language).fallbacks('en').get(user=self.request.user.pk, deleted=False,
                                                                         user__is_active=True)
        self.check_object_permissions(self.request, obj)
        return obj


class ProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.kwargs['user']
        obj = UserProfile.objects.language().fallbacks('en').get(user=user, deleted=False, user__is_active=True)
        return obj


class UserSettingsView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    # queryset = UserProfile.objects.language().fallbacks('en').all()
    serializer_class = UserSettingsSerializer

    def get_object(self):
        obj = UserProfile.objects.language('en').get(user=self.request.user.pk, deleted=False,
                                                     user__is_active=True)
        self.check_object_permissions(self.request, obj)
        # self.check_object_permissions(self.request, obj)
        return obj


class UserProfileCheckView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, userauth, locale):

        username = userauth

        try:
            profile = UserProfile.objects.language().fallbacks('en').get(user__username=username, deleted=False,
                                                                         user__is_active=True)
        except UserProfile.DoesNotExist:

            try:
                profile = UserProfile.objects.language().fallbacks('en').get(user__username=username, deleted=False,
                                                                             user__is_active=True)
            except UserProfile.DoesNotExist:

                profile = None

        serializer = UserProfileSerializer(profile, context={'request': request})

        return Response(serializer.data)


class ShortUserProfileView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileShortSerializer

    def get_object(self):
        user = self.kwargs['user']

        obj = UserProfile.objects.language().fallbacks('en').get(user_id=user, deleted=False, user__is_active=True)

        return obj


class ShortUserProfileBySlugView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        slug = self.kwargs['slug']

        obj = get_object_or_404(UserProfile.objects.language().fallbacks('en'), slug__iexact=slug, deleted=False,
                                user__is_active=True)
        return obj


class UserProfileCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = UserProfileCategorySerializer

    def get_queryset(self):
        profile = self.kwargs['profile']
        interest = self.kwargs['interest']

        return UserProfileCategory.objects.filter(profile=profile, profile_category=True, interest=interest)


class AllUserProfileCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = UserProfileCategorySerializer

    def get_queryset(self):
        profile = self.kwargs['profile']
        interest = self.kwargs['interest']

        return UserProfileCategory.objects.filter(profile=profile, interest=interest)


class ChildUserProfileCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = UserProfileCategorySerializer

    def get_queryset(self):
        profile = self.kwargs['profile']
        interest = self.kwargs['interest']
        parent = int(self.kwargs['parent'])
        if parent == 0:
            return UserProfileCategory.objects.filter(category__parent__isnull=True, profile=profile, interest=interest)
        else:
            return UserProfileCategory.objects.filter(category__parent=parent, profile=profile, interest=interest)


class CreateUserProfileCategoryView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)

    def post(self, request, *args, **kwargs):

        profile = request.data['profile']
        interest = request.data['interest']
        category = request.data['category']

        try:
            object = UserProfileCategory.objects.get(profile=profile, category=category,
                                                     interest=interest)

            self.check_object_permissions(self.request, object)
            object.profile_category = True
            object.save()
        except:
            object = UserProfileCategory(profile_id=profile, category_id=category, interest=interest,
                                         profile_category=True)
            self.check_object_permissions(self.request, object)
            object.save()

        serializer = UserProfileCategorySerializer(object, context={'request': request})

        return Response(serializer.data)


class DeleteUserProfileCategoryView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)

    def delete(self, request, profile, category, format=None):

        object = UserProfileCategory.objects.get(profile=profile, category=category,
                                                 interest=True, profile_category=True)

        self.check_object_permissions(self.request, object)

        exist = UserProfileCategory.objects.filter(profile=profile, category=category,
                                                   interest=True).exists()

        if exist:
            object.profile_category = False
            object.save()
        else:
            object.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProfileCategoriesForSelectView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    serializer_class = CategorySerializer

    def get_queryset(self):
        name = self.kwargs['name']
        profile = self.kwargs['profile']
        interest = self.kwargs['interest']

        return Category.objects.language().filter(name_with_parent__icontains=name, approved=True).exclude(
            id__in=UserProfileCategory.objects.filter(profile=profile, profile_category=True,
                                                      interest=interest).values_list('category', flat=True))


class UserProfileCountryInterestsView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = UserProfileCountryInterestSerializer

    def get_queryset(self):
        profile = self.kwargs['profile']

        return UserProfileCountryInterest.objects.filter(profile=profile)


class CreateUserProfileCountryInterestView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    serializer_class = UserProfileCountryInterestSerializer
    queryset = UserProfileCountryInterest.objects.all()


class DeleteUserProfileCountryInterestView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    serializer_class = UserProfileCountryInterestSerializer

    def get_object(self):
        profile = self.kwargs['profile']
        country = self.kwargs['country']
        object = UserProfileCountryInterest.objects.get(profile=profile, country=country)
        self.check_object_permissions(self.request, object)
        return object


class UserProfilesByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileShortSerializer

    def get_queryset(self):

        page = int(self.kwargs['page'])

        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        region = self.request.GET.get('region', None)
        city = self.request.GET.get('city', None)
        tag = self.request.GET.get('tag', None)
        industry = self.request.GET.get('industry', None)
        type = self.request.GET.get('type', None)
        size = self.request.GET.get('size', None)
        keyword = self.request.GET.get('keyword', None)
        company = self.request.GET.get('company', None)
        follow_company = self.request.GET.get('follow_company', None)
        follow_profile = self.request.GET.get('follow_profile', None)
        following_user = self.request.GET.get('following_user', None)
        community = self.request.GET.get('community', None)
        company_admin = self.request.GET.get('company_admin', None)
        community_admin = self.request.GET.get('community_admin', None)
        title = self.request.GET.get('title', None)
        ordering = self.request.GET.get('ordering', None)
        latitude = self.request.GET.get('latitude', None)
        longitude = self.request.GET.get('longitude', None)

        # if (keyword is not None and community is None) or ordering == 'close':
        #
        #     s = ProfileDocument.search()
        #     if keyword is not None:
        #         filter_list = Qel("multi_match", query=keyword, fields=['name',
        #                                                                 'description',
        #                                                                 'headline',
        #                                                                 'tags',
        #                                                                 'employment'
        #                                                                 ])
        #     else:
        #         filter_list = Qel()
        #     filter_list = filter_list & Qel('match', is_active=True)
        #     filter_list = filter_list & Qel('match', deleted=False)
        #     if country is not None:
        #         filter_list = filter_list & Qel('match', country=country)
        #     if region is not None:
        #         filter_list = filter_list & Qel('match', region=region)
        #     if city is not None:
        #         filter_list = filter_list & Qel('match', city=city)
        #     if industry is not None:
        #         filter_list = filter_list & Qel('match', company_industry=industry)
        #     if type is not None:
        #         filter_list = filter_list & Qel('match', company_type=type)
        #     if size is not None:
        #         filter_list = filter_list & Qel('match', company_size=size)
        #
        #     if category is not None:
        #         filter_list = filter_list & Qel('match', categories=category)
        #
        #     ordering_code = get_elastic_ordering(ordering, latitude, longitude)
        #     s = s.query(filter_list).sort(*ordering_code)
        #
        #     if page == 0:
        #         s = s[:20]
        #     else:
        #         item_from = page * 20
        #         item_to = page * 20 + 20
        #         s = s[item_from:item_to]
        #
        #     response = s.execute()
        #     response_dict = response.to_dict()
        #
        #     hits = response_dict['hits']['hits']
        #     objects = []
        #     for hit in hits:
        #         if (hit['_source']['deleted'] == False):
        #             try:
        #                 obj = UserProfile.objects.language().fallbacks('en').get(id=hit['_id'])
        #                 objects.append(obj)
        #             except UserProfile.DoesNotExist:
        #                 pass

        # else:

        filter_list = Q(user__is_active=True, deleted=False)
        if keyword is not None:
            filter_list &= Q(full_name__icontains=keyword) | Q(short_description__icontains=keyword) | Q(
                headline__icontains=keyword)

        if category is not None:
            filter_list = filter_list & Q(user_categories__category=category)
        if industry is not None:
            filter_list = filter_list & Q(employment__company__company_industry=industry)
        if type is not None:
            filter_list = filter_list & Q(employment__company__company_type=type)
        if size is not None:
            filter_list = filter_list & Q(employment__company__company_size=size)

        if country is not None:
            filter_list = filter_list & Q(country=country)
        if city is not None:
            filter_list = filter_list & Q(city=city)
        if region is not None:
            filter_list = filter_list & Q(city__region=region)
        if company is not None:
            filter_list = filter_list & Q(employment__company=company, employment__education=False)
        if company_admin is not None:
            filter_list = filter_list & Q(user__managed_companies__company=company_admin)

        if follow_company is not None:
            filter_list = filter_list & Q(user__following_companies__company=follow_company)
        if follow_profile is not None:
            filter_list = filter_list & Q(user__following_profiles__profile=follow_profile)
        if following_user is not None:
            filter_list = filter_list & Q(followers__user=following_user)

        if community_admin is not None:
            filter_list = filter_list & (
                    Q(user__communities__community=community_admin) & Q(user__communities__admin=True))

        if title is not None:
            filter_list = filter_list & Q(employment__title__icontains=title)
        if tag is not None:
            tag = tag.lower()
            filter_list = filter_list & Q(tags__name__iexact=tag)

        if community is not None:

            filter_list = filter_list & Q(user__communities__community=community)

            if keyword is not None:
                filter_list = filter_list & (Q(full_name__icontains=keyword) | Q(slug__icontains=keyword))

        ordering_code = get_ordering(ordering)

        if page == 0:
            objects = UserProfile.objects.language().fallbacks('en').filter(filter_list).order_by(
                *ordering_code)[:20]
            if not objects:
                objects = UserProfile.objects.language('en').filter(
                    filter_list).order_by(*ordering_code)[:20]


        else:

            item_from = page * 20
            item_to = page * 20 + 20
            objects = UserProfile.objects.language().fallbacks('en').filter(
                filter_list).order_by(*ordering_code)[
                      item_from:item_to]
            if not objects:
                objects = UserProfile.objects.language('en').filter(
                    filter_list).order_by(*ordering_code)[item_from:item_to]

        return objects


def form_suggestions_array(objects, suggestions, type):
    for obj in objects:
        image = None
        if type == 'user':
            if obj.img:
                image = get_thumbnail(obj.img.file, '100x100', crop='center', quality=99).url

            name = obj.full_name
        else:
            name = obj.name
        if type == 'company':
            if obj.logo:
                image = get_thumbnail(obj.logo.file, '100x100', crop='center', quality=99).url
        if type == 'category':
            if obj.image:
                image = get_thumbnail(obj.image, '100x100', crop='center', quality=99).url
        if type == 'community':
            if obj.image:
                image = get_thumbnail(obj.image.file, '100x100', crop='center', quality=99).url

        if type == 'product':
            if obj.images:
                image_obj = obj.images.first()
                image = get_thumbnail(image_obj.image.file, '100x100', crop='center', quality=99).url

        if type != 'product' and type != 'community':
            slug = obj.slug
        else:
            slug = ''

        suggestion = {'id': obj.id, 'slug': slug, 'name': name, 'image': image,
                      'type': type}
        suggestions.append(suggestion)
    return suggestions


class SuggestionsView(APIView):
    permission_classes = (AllowAny,)

    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, keyword):

        suggestions = []
        filter_list = (Q(name__icontains=keyword) | Q(slug__icontains=keyword))
        filter_list = filter_list & (Q(products_exist=True) | Q(posts_exist=True) | Q(communities_exist=True))
        try:
            objects = Category.objects.language().filter(filter_list).order_by('name')[:5]
        except ObjectDoesNotExist:
            objects = []

        if objects:
            suggestions = form_suggestions_array(objects, suggestions, 'category')

        lang_len = len(objects)

        if lang_len < 5:
            ids = []
            for obj in objects:
                ids.append(obj.id)
            try:
                objects = Category.objects.language('en').filter(filter_list).exclude(id__in=ids).order_by('name')[
                          :(5 - lang_len)]
            except ObjectDoesNotExist:
                objects = []

            if objects:
                suggestions = form_suggestions_array(objects, suggestions, 'category')

        filter_list = Q(deleted=False)

        filter_list = filter_list & (Q(full_name__icontains=keyword) | Q(slug__icontains=keyword))
        try:
            objects = UserProfile.objects.language().fallbacks('en').filter(filter_list).order_by('full_name')[:5]
        except ObjectDoesNotExist:
            objects = []
        if objects:
            suggestions = form_suggestions_array(objects, suggestions, 'user')

        lang_len = len(objects)
        if lang_len < 5:
            ids = []
            for obj in objects:
                ids.append(obj.id)
            try:
                objects = UserProfile.objects.language('en').filter(filter_list).exclude(id__in=ids).order_by(
                    'first_name',
                    'last_name')[
                          :(5 - lang_len)]
            except ObjectDoesNotExist:
                objects = []

            if objects:
                suggestions = form_suggestions_array(objects, suggestions, 'user')

        filter_list = (Q(name__icontains=keyword) | Q(slug__icontains=keyword))
        filter_list = filter_list & Q(deleted=False)

        try:
            objects = Company.objects.language().fallbacks('en').filter(filter_list).order_by('name')[:5]
        except ObjectDoesNotExist:
            objects = []

        if objects:
            suggestions = form_suggestions_array(objects, suggestions, 'company')

        lang_len = len(objects)

        if lang_len < 5:
            ids = []
            for obj in objects:
                ids.append(obj.id)
            try:
                objects = Company.objects.language('en').filter(filter_list).exclude(id__in=ids).order_by('name')[
                          :(5 - lang_len)]
            except ObjectDoesNotExist:
                objects = []
            if objects:
                suggestions = form_suggestions_array(objects, suggestions, 'company')

        if len(suggestions) < 15 and request.user.pk:
            filter_list = (Q(name__icontains=keyword))
            filter_list = filter_list & Q(deleted=False)

            objects = Community.objects.language().filter(filter_list).order_by('name')[:5]

            if objects:
                suggestions = form_suggestions_array(objects, suggestions, 'community')

            lang_len = len(objects)

            if lang_len < 5:
                ids = []
                for obj in objects:
                    ids.append(obj.id)
                try:
                    objects = Community.objects.language('en').filter(filter_list).exclude(id__in=ids).order_by('name')[
                              :(5 - lang_len)]
                except ObjectDoesNotExist:
                    objects = []

                if objects:
                    suggestions = form_suggestions_array(objects, suggestions, 'community')

        if len(suggestions) < 15:
            filter_list = (Q(name__icontains=keyword))
            filter_list = filter_list & Q(deleted=False, published=True)
            try:
                objects = Product.objects.language().filter(filter_list).order_by('name')[:5]
            except ObjectDoesNotExist:
                objects = []

            if objects:
                suggestions = form_suggestions_array(objects, suggestions, 'product')

            lang_len = len(objects)

            if lang_len < 5:
                ids = []
                for obj in objects:
                    ids.append(obj.id)
                try:
                    objects = Product.objects.language('en').filter(filter_list).exclude(id__in=ids).order_by('name')[
                              :(5 - lang_len)]
                except ObjectDoesNotExist:
                    objects = []
                if objects:
                    suggestions = form_suggestions_array(objects, suggestions, 'product')

        if len(suggestions) < 15:
            filter_list = Q(name__icontains=keyword.lower())
            try:
                objects = Tag.objects.filter(filter_list).order_by('name')[:5]
            except ObjectDoesNotExist:
                objects = []

            if objects:
                suggestions = form_suggestions_array(objects, suggestions, 'tag')

        return Response(suggestions)


class UserProfilesCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        keyword = self.request.GET.get('keyword', None)
        company = self.request.GET.get('company', None)
        title = self.request.GET.get('title', None)

        filter_list = Q(deleted=False, user__is_active=True)
        if category is not None:
            filter_list = filter_list & Q(categories__category=category)
        if country is not None:
            filter_list = filter_list & Q(country=country)
        if city is not None:
            filter_list = filter_list & Q(city=city)
        if company is not None:
            filter_list = filter_list & Q(employment__company=company)
        if title is not None:
            filter_list = filter_list & Q(employment__title__icontains=title)
        if keyword is not None:
            filter_list = filter_list & (
                    Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(
                headline__icontains=keyword) | Q(
                short_description__icontains=keyword) | Q(employment__title__icontains=keyword) | Q(
                employment__company_name__icontains=keyword))

        count = UserProfile.objects.language().fallbacks('en').filter(filter_list).count()

        data = {'count': count}

        return Response(data)


class UserProfileFollowersView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileFollowerSerializer

    def get_queryset(self):
        profile = self.kwargs['profile']

        return UserProfileFollower.objects.filter(profile=profile, profile__deleted=False, user__is_active=True)


class FollowingUserProfilesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileFollowerSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        return UserProfileFollower.objects.filter(user=user, profile__deleted=False, user__is_active=True)


class FollowUserProfileView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    queryset = UserProfileFollower.objects.all()
    serializer_class = UserProfileFollowerSerializer


class UnfollowUserProfileView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = UserProfileFollowerSerializer

    def get_object(self):
        user = self.kwargs['user']
        profile = self.kwargs['profile']
        object = UserProfileFollower.objects.get(profile=profile, user=user)

        self.check_object_permissions(self.request, object)
        return object


class CheckFollowingUserProfile(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = self.request.GET.get('profile', None)
        user = self.request.GET.get('user', None)

        res = UserProfileFollower.objects.filter(profile=profile, user=user, profile__deleted=False,
                                                 user__is_active=True).exists()

        data = {'following': res}

        return Response(data)


class CheckProfileSlugView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, slug):
        # slug = self.request.GET.get('slug', None)

        res = UserProfile.objects.language().fallbacks('en').filter(slug__iexact=slug, deleted=False,
                                                                    user__is_active=True).exists()

        data = {'exists': res}

        return Response(data)


class SearchProfilesByNameView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserProfileShortSerializer

    def get_queryset(self):
        name = self.kwargs['name']
        company = self.request.GET.get('company', None)
        community = self.request.GET.get('community', None)

        filter_list = Q(deleted=False, user__is_active=True)

        if company is not None:
            filter_list = filter_list & Q(employment__company=company, employment__present_time=True,
                                          employment__education=False)
        if community is not None:
            filter_list = filter_list & Q(user__communities__community=community)

        filter_list = filter_list & (Q(full_name__icontains=name) | Q(slug__icontains=name))

        objects = UserProfile.objects.language().fallbacks('en').filter(filter_list).order_by('full_name')

        if not objects:
            objects = UserProfile.objects.language('en').filter(filter_list).order_by('full_name')

        if company is not None:
            objects = objects.exclude(
                user__in=CompanyUser.objects.filter(company=company).values_list('user'))
        return objects


class SetSeenNotificationsView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        try:
            request.user.user_profile.eventsqty.notifications = 0
            request.user.user_profile.eventsqty.save()
        except ObjectDoesNotExist:
            pass

        return Response({'res': True})


class CreateResumeView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    serializer_class = ResumeSerializer
    queryset = Resume.objects.all()

    def post(self, request, *args, **kwargs):
        profile = request.data['profile']
        show_in_profile = request.data['show_in_profile']
        file = request.data['file']

        object = Resume(profile_id=profile, show_in_profile=show_in_profile, file_id=file)
        self.check_object_permissions(self.request, object)
        object.save()

        serializer = ResumeSerializer(object, context={'request': request})

        return Response(serializer.data)


class DeleteResumeView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)
    serializer_class = ResumeSerializer
    queryset = Resume.objects.all()


class ProfileResumesView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ResumeSerializer

    def get_queryset(self):
        profile = self.request.user.user_profile
        return Resume.objects.filter(profile=profile).order_by('id')


class ProfileAllowedResumesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ResumeSerializer

    def get_queryset(self):
        profile = self.kwargs['profile']
        return Resume.objects.filter(profile=profile, show_in_profile=True)


class SetResumePublicStatus(APIView):
    permission_classes = (IsAuthenticated, IsOwnerDetails)

    def put(self, request, pk, status):
        try:
            obj = Resume.objects.get(pk=pk)
            self.check_object_permissions(self.request, obj)
            if int(status) == 1:
                obj.show_in_profile = True
            else:
                obj.show_in_profile = False
            obj.save()

        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'res': obj.show_in_profile})


class TotalEventsQtyView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        new_messages = self.request.user.user_profile.eventsqty.new_messages
        notifications = self.request.user.user_profile.eventsqty.notifications
        new_job_responds = self.request.user.user_profile.eventsqty.new_job_responds
        new_offering_reponds = self.request.user.user_profile.eventsqty.new_offering_reponds
        new_request_responds = self.request.user.user_profile.eventsqty.new_request_responds
        new_customer_requests = self.request.user.user_profile.eventsqty.new_customer_requests
        your_open_supply_requests = self.request.user.user_profile.eventsqty.your_open_supply_requests
        your_open_offering_responds = self.request.user.user_profile.eventsqty.your_open_offering_responds
        your_open_request_responds = self.request.user.user_profile.eventsqty.your_open_request_responds
        your_open_job_responds = self.request.user.user_profile.eventsqty.your_open_job_responds

        user_companies = CompanyUser.objects.filter(user=self.request.user)

        for user_company in user_companies:
            new_job_responds = new_job_responds + user_company.company.eventsqty.new_job_responds
            new_offering_reponds = new_offering_reponds + user_company.company.eventsqty.new_offering_reponds
            new_request_responds = new_request_responds + user_company.company.eventsqty.new_request_responds
            new_customer_requests = new_customer_requests + user_company.company.eventsqty.new_customer_requests
            your_open_supply_requests = your_open_supply_requests + user_company.company.eventsqty.your_open_supply_requests
            your_open_offering_responds = your_open_offering_responds + user_company.company.eventsqty.your_open_offering_responds
            your_open_request_responds = your_open_request_responds + user_company.company.eventsqty.your_open_request_responds
            new_messages = new_messages + user_company.company.eventsqty.new_messages

        data = {
            'new_messages': new_messages,
            'notifications': notifications,
            'new_job_responds': new_job_responds,
            'new_offering_reponds': new_offering_reponds,
            'new_request_responds': new_request_responds,
            'new_customer_requests': new_customer_requests,
            'your_open_supply_requests': your_open_supply_requests,
            'your_open_offering_responds': your_open_offering_responds,
            'your_open_request_responds': your_open_request_responds,
            'your_open_job_responds': your_open_job_responds

        }

        return Response(data)
