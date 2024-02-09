from .serializers import CompanySizeSerializer, CompanyIndustrySerializer, CompanyTypeSerializer, \
    CompanyCategorySerializer, CompanySerializer, CompanyUserSerializer, CompanyShortSerializer, \
    CompanyFollowerSerializer, FavoriteCompanySerializer
from rest_framework import generics
from rest_framework.views import APIView
from .models import Company, CompanyCategory, CompanyUser, CompanyIndustry, CompanySize, CompanyType, CompanyFollower, \
    FavoriteCompany
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from .permissions import IsOwnerOrCompanyAdmin, IsOwnerOrCompanyAdminDetails, IsUserOrCompanyAdmin, IsOwner
from django.shortcuts import get_object_or_404
# from elasticsearch_dsl import Q as Qel
from .documents import CompanyDocument
from hvad.utils import get_translation

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


def get_ordering(code, parent_model=''):
    if parent_model == 'company__':
        ordering = ['-create_date', '-id']
    else:
        ordering = ['-' + parent_model + 'update_date', '-' + parent_model + 'eventsqty__followers', '-id']

    if code == 'rating':
        ordering = ['-' + parent_model + 'eventsqty__rating', '-' + parent_model + 'eventsqty__related_reviews',
                    '-' + parent_model + 'eventsqty__followers', '-id']

    if code == 'popularity' or code == 'close':
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


class CompanyCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CompanyCategorySerializer

    def get_queryset(self):
        company = self.kwargs['company']
        interest = self.kwargs['interest']
        parent = int(self.kwargs['parent'])
        if parent == 0:
            return CompanyCategory.objects.filter(category__parent__isnull=True, company=company, interest=interest)
        else:
            return CompanyCategory.objects.filter(category__parent=parent, company=company, interest=interest)


class CompanyTypesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyTypeSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CompanyTypesView, self).dispatch(*args, **kwargs)

    queryset = CompanyType.objects.language().all().order_by('position')


class CompanySizesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySizeSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CompanySizesView, self).dispatch(*args, **kwargs)

    queryset = CompanySize.objects.language().all().order_by('position')


class CompanyIndustriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyIndustrySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CompanyIndustriesView, self).dispatch(*args, **kwargs)

    queryset = CompanyIndustry.objects.language().all().order_by('name')


class CreateCompanyCategoryView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdminDetails)

    def post(self, request, *args, **kwargs):
        company = request.data['company']

        category = request.data['category']

        CompanyCategory.objects.filter(company=company).delete()
        object = CompanyCategory(company_id=company, category_id=category, product_category=True)
        object.save()

        serializer = CompanyCategorySerializer(object, context={'request': request})

        return Response(serializer.data)


class CompaniesByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyShortSerializer

    @method_decorator(cache_page(60 * 10))
    @method_decorator(vary_on_cookie)
    def dispatch(self, *args, **kwargs):
        return super(CompaniesByPageView, self).dispatch(*args, **kwargs)

    def get_queryset(self):

        page = int(self.kwargs['page'])
        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        industry = self.request.GET.get('company_industry', None)
        type = self.request.GET.get('company_type', None)
        size = self.request.GET.get('company_size', None)
        tag = self.request.GET.get('tag', None)
        community = self.request.GET.get('community', None)
        keyword = self.request.GET.get('keyword', None)
        latitude = self.request.GET.get('latitude', None)
        longitude = self.request.GET.get('longitude', None)
        ordering = self.request.GET.get('ordering', None)

        # if (keyword is not None) or ordering == 'close':
        #
        #     s = CompanyDocument.search()
        #     if keyword is not None:
        #         filter_list = Qel("multi_match", query=keyword, fields=['name',
        #                                                                 'description',
        #                                                                 'headline',
        #                                                                 'tags',
        #                                                                 'address',
        #                                                                 'sales_email',
        #                                                                 'business_email',
        #                                                                 'website',
        #                                                                 'city_name',
        #                                                                 'address',
        #                                                                 'phone_number',
        #                                                                 'postal_code'
        #
        #                                                                 ])
        #     else:
        #         filter_list = Qel()
        #     filter_list = filter_list & filter_list & Qel('match', deleted=False)
        #     if country is not None:
        #         filter_list = filter_list & Qel('match', country=country)
        #     if city is not None:
        #         filter_list = filter_list & Qel('match', city=city)
        #     if region is not None:
        #         filter_list = filter_list & Qel('match', region=region)
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
        #
        #     s = s.query(filter_list).sort(*ordering_code)
        #
        #     if page == 0:
        #         s = s[:10]
        #     else:
        #         item_from = page * 10
        #         item_to = page * 10 + 10
        #         s = s[item_from:item_to]
        #
        #     response = s.execute()
        #     response_dict = response.to_dict()
        #
        #     hits = response_dict['hits']['hits']
        #
        #     objects = []
        #     for hit in hits:
        #         try:
        #             obj = Company.objects.language().fallbacks('en').get(id=hit['_id'])
        #             objects.append(obj)
        #         except Company.DoesNotExist:
        #             pass
        #     # ids = [hit['_id'] for hit in hits]
        #     # ordering_code = get_ordering(ordering)
        #     # objects = Company.objects.language().fallbacks('en').filter(id__in=ids).order_by(*ordering_code)

        filter_list = Q(deleted=False)

        if keyword is not None:
            filter_list &= Q(name__icontains=keyword) | Q(short_description__icontains=keyword) | Q(
                headline__icontains=keyword)

        if category is not None:
            filter_list &= Q(categories__category=category)
        if country is not None:
            filter_list = filter_list & Q(country=country)
        if city is not None:
            filter_list = filter_list & Q(city=city)
        if region is not None:
            filter_list = filter_list & Q(city__region=region)
        if industry is not None:
            filter_list = filter_list & Q(company_industry=industry)
        if type is not None:
            filter_list = filter_list & Q(company_type=type)
        if size is not None:
            filter_list = filter_list & Q(company_size=size)
        if tag is not None:
            tag = tag.lower()
            filter_list = filter_list & Q(tags__name__iexact=tag)
        if community is not None:
            filter_list = filter_list & Q(communities__community=community)

        ordering_code = get_ordering(ordering)
        if page == 0:
            objects = Company.objects.language().fallbacks('en').filter(filter_list).order_by(*ordering_code)[:10]

        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = Company.objects.language().fallbacks('en').filter(filter_list).order_by(*ordering_code)[
                      item_from:item_to]

        return objects


class CompaniesCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        industry = self.request.GET.get('industry', None)
        type = self.request.GET.get('type', None)
        size = self.request.GET.get('size', None)
        tag = self.request.GET.get('tag', None)
        search_word = self.request.GET.get('search_word', None)

        if search_word is not None:

            s = CompanyDocument.search()
            filter_list = Qel("multi_match", query=search_word, fields=['name',
                                                                        'description',
                                                                        'headline',
                                                                        'tags',
                                                                        'address',
                                                                        'sales_email',
                                                                        'business_email',
                                                                        'website',
                                                                        'city_name',
                                                                        'address',
                                                                        'phone_number',
                                                                        'postal_code'

                                                                        ])
            filter_list = filter_list & Qel('match', deleted=False)
            if country is not None:
                filter_list = filter_list & Qel('match', country=country)
            if city is not None:
                filter_list = filter_list & Qel('match', city=city)
            if region is not None:
                filter_list = filter_list & Qel('match', city__region=region)
            if industry is not None:
                filter_list = filter_list & Qel('match', company_industry=industry)
            if type is not None:
                filter_list = filter_list & Qel('match', company_type=type)
            if size is not None:
                filter_list = filter_list & Qel('match', company_size=size)

            s = s.query(filter_list)

            count = s.count()

        else:

            filter_list = Q(deleted=False)

            if category is not None:
                filter_list = filter_list & Q(categories__category=category)
            if country is not None:
                filter_list = filter_list & Q(country=country)
            if city is not None:
                filter_list = filter_list & Q(city=city)
            if region is not None:
                filter_list = filter_list & Q(city__region=region)
            if industry is not None:
                filter_list = filter_list & Q(company_industry=industry)
            if type is not None:
                filter_list = filter_list & Q(company_type=type)
            if size is not None:
                filter_list = filter_list & Q(company_size=size)
            if tag is not None:
                tag = tag.lower()
                filter_list = filter_list & Q(tags__name__in=[tag])

            count = Company.objects.language().fallbacks('en').filter(filter_list).count()

        data = {'count': count}

        return Response(data)


class CompanyDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Company.objects.language().fallbacks('en').filter(deleted=False)
    serializer_class = CompanySerializer


class CompanyDetailsShortView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Company.objects.language().fallbacks('en').filter(deleted=False)
    serializer_class = CompanyShortSerializer


class CompanyDetailsInLanguageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySerializer

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        object = Company.objects.language(language).fallbacks('en').get(pk=pk, deleted=False)
        return object


class CheckCompanyBySlugView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        slug = self.request.GET.get('slug', None)

        res = Company.objects.language().fallbacks('en').filter(slug__iexact=slug, deleted=False).exists()

        data = {'exists': res}

        return Response(data)


class CompanyBySlugView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySerializer

    def get_object(self):
        slug = self.kwargs['slug']

        obj = get_object_or_404(Company.objects.language().fallbacks('en'), slug__iexact=slug, deleted=False)
        return obj


class CompanyBySlugInLanguageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanySerializer

    def get_object(self):
        slug = self.kwargs['slug']
        language = self.kwargs['language']
        # try:
        # object = Company.objects.language(language).fallbacks('en').get(slug__iexact=slug)
        object = get_object_or_404(Company.objects.language(language).fallbacks('en'), slug__iexact=slug, deleted=False)

        # except:
        #     return Response(None)
        return object


class CompaniesByNameView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyShortSerializer

    def get_queryset(self):
        language = self.kwargs['language']
        name = self.kwargs['name']
        return Company.objects.language(language).filter(name=name, deleted=False)


class SearchCompaniesByNameView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyShortSerializer

    def get_queryset(self):
        name = self.kwargs['name']
        education = self.request.GET.get('education', None)

        filter_list = (Q(name__icontains=name) | Q(slug__icontains=name))
        filter_list = filter_list & Q(deleted=False)
        if education is not None:
            filter_list = filter_list & Q(company_type=4)

        objects = Company.objects.language().filter(filter_list).order_by('name')

        if not objects:
            objects = Company.objects.language('en').filter(filter_list).order_by('name')

        return objects


class DeleteCompanyView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)

    def delete(self, request, pk):
        company = Company.objects.language('en').get(pk=pk)
        self.check_object_permissions(self.request, company)

        company.smart_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateCompanyDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)

    serializer_class = CompanySerializer

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        obj = Company.objects.language(language).fallbacks('en').get(pk=pk, deleted=False)
        self.check_object_permissions(self.request, obj)

        return obj


class CreateCompanyView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = CompanySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            company_user = CompanyUser(company_id=serializer.data['id'], user=request.user, admin=True, sales=True,
                                       supply=True)
            company_user.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyUsersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyUserSerializer

    def get_queryset(self):
        company = self.kwargs['company']
        queryset = CompanyUser.objects.filter(company=company, company__deleted=False)
        return queryset


class CreateCompanyUserView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdminDetails)
    serializer_class = CompanyUserSerializer
    queryset = CompanyUser.objects.all()

    def perform_create(self, serializer):
        self.check_object_permissions(self.request, CompanyUser(company=serializer.validated_data.get('company')))
        serializer.save()


class UserCompaniesView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyUserSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        queryset = CompanyUser.objects.filter(user=user, company__deleted=False)
        return queryset


class UserCompaniesNotInCommunityView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyUserSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        community = self.kwargs['community']
        queryset = CompanyUser.objects.filter(user=user, admin=True, company__deleted=False).exclude(
            company__communities__community_id=community).exclude(company__invitations__community_id=community)
        return queryset


class UserCompaniesInCommunityView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyUserSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        community = self.kwargs['community']
        queryset = CompanyUser.objects.filter(user=user, admin=True, company__communities__community_id=community,
                                              company__deleted=False)
        return queryset


class UserPermisionsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompanyUserSerializer

    def get_object(self):
        user = self.kwargs['user']
        company = self.kwargs['company']
        try:
            object = CompanyUser.objects.get(company=company, user=user, company__deleted=False)
        except:
            object = None
        return object


class CompanyUserUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdminDetails)
    serializer_class = CompanyUserSerializer

    def get_object(self):
        company = self.kwargs['company']
        user = self.kwargs['user']
        object = CompanyUser.objects.get(company=company, user=user, company__deleted=False)
        self.check_object_permissions(self.request, object)
        return object


class CompanyFollowersView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyFollowerSerializer

    def get_queryset(self):
        company = self.kwargs['company']

        return CompanyFollower.objects.filter(company=company, company__deleted=False)


class FollowingCompaniesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CompanyFollowerSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        return CompanyFollower.objects.filter(user=user, company__deleted=False)


class FollowCompanyView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)
    queryset = CompanyFollower.objects.all()
    serializer_class = CompanyFollowerSerializer


class UnfollowCompanyView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsUserOrCompanyAdmin)
    serializer_class = CompanyFollowerSerializer

    def get_object(self):
        user = self.kwargs['user']
        company = self.kwargs['company']
        object = CompanyFollower.objects.get(company=company, user=user)

        self.check_object_permissions(self.request, object)
        return object


class CheckFollowingCompany(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        company = self.request.GET.get('company', None)
        user = self.request.GET.get('user', None)

        res = CompanyFollower.objects.filter(company=company, user=user, company__deleted=False).exists()

        data = {'following': res}

        return Response(data)


class CheckDeleteCompanyAdminStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user

        companies = CompanyUser.objects.filter(user=user, company__deleted=False)

        for company in companies.all():
            count = CompanyUser.objects.filter(company=company.company, user__is_active=True).exclude(user=user).count()
            if not count:
                translation = get_translation(company.company, 'en')
                return Response({'status': False, 'company': translation.name})

        return Response({'status': True})


class CreateFavoriteCompanyView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = FavoriteCompany.objects.all()
    serializer_class = FavoriteCompanySerializer


class DeleteFavoriteCompanyView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = FavoriteCompanySerializer

    def get_object(self):
        company = self.kwargs['company']

        obj = FavoriteCompany.objects.get(company=company, user=self.request.user)
        self.check_object_permissions(self.request, obj)

        return obj


class FavoriteCompaniesByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteCompanySerializer

    def get_queryset(self):

        page = int(self.kwargs['page'])
        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        industry = self.request.GET.get('company_industry', None)
        type = self.request.GET.get('company_type', None)
        size = self.request.GET.get('company_size', None)
        ordering = self.request.GET.get('ordering', None)

        filter_list = Q(user=self.request.user)
        filter_list = filter_list & Q(company__deleted=False)
        if country is not None:
            filter_list = filter_list & Q(company__country=country)
        if city is not None:
            filter_list = filter_list & Q(company__city=city)
        if region is not None:
            filter_list = filter_list & Q(company__city__region=region)
        if category is not None:
            filter_list = filter_list & Q(company__categories__category=category)
        if industry is not None:
            filter_list = filter_list & Q(company__company_industry=industry)
        if type is not None:
            filter_list = filter_list & Q(company__company_type=type)
        if size is not None:
            filter_list = filter_list & Q(company__company_size=size)

        ordering_code = get_ordering(ordering, 'company__')
        objects = FavoriteCompany.objects.filter(filter_list).order_by(*ordering_code)

        if page == 0:
            objects = objects[:10]
        else:
            item_from = page * 10
            item_to = page * 10 + 10
            objects = objects[item_from:item_to]

        return objects
