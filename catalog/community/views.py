from .serializers import CommunityCategorySerializer, CommunityCompanySerializer, CommunityInvitationSerializer, \
    CommunityMemberSerializer, CommunitySerializer
from rest_framework import generics
from rest_framework.views import APIView
from .models import CommunityInvitation, CommunityMember, CommunityCategory, CommunityCompany, Community
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from .permissions import IsOwnerOrCommunityAdmin, \
    IsOwnerOrCommunityAdminDetails, IsInvitationUser, IsOpenCommunityOrAdmin, IsUserOrAdmin, \
    IsCompanyAdminOrCommunityAdmin
from .documents import CommunityDocument
# from elasticsearch_dsl import Q as Qel
from hvad.utils import get_translation


def get_ordering(code, parent_model=''):
    if parent_model == 'community__':
        ordering = ['-update_date', '-id']
    else:
        ordering = ['-' + parent_model + 'update_date', '-' + parent_model + 'eventsqty__members', '-id']

    if code == 'popularity':
        ordering = ['-' + parent_model + 'eventsqty__members', '-id']

    return ordering


def get_elastic_ordering(code):
    ordering = ['-update_date', '-members']

    if code == 'popularity':
        ordering = ['-members', '-update_date']

    return ordering


class DeleteCommunityView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdmin)

    def delete(self, request, pk):
        community = Community.objects.language('en').get(pk=pk)
        self.check_object_permissions(self.request, community)
        community.smart_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommunityParentCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CommunityCategorySerializer

    def get_queryset(self):
        community = self.kwargs['community']
        parent = int(self.kwargs['parent'])
        if parent == 0:
            return CommunityCategory.objects.filter(category__parent__isnull=True, community=community)
        else:
            return CommunityCategory.objects.filter(category__parent=parent, community=community)


class CommunityCategoriesView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CommunityCategorySerializer

    def get_queryset(self):
        community = self.kwargs['community']

        return CommunityCategory.objects.filter(community=community, community_category=True)


class CreateCommunityCategoryView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)

    def post(self, request, *args, **kwargs):

        community = request.data['community']
        category = request.data['category']

        try:
            obj = CommunityCategory.objects.get(community=community, category=category)

            self.check_object_permissions(self.request, obj)
            obj.community_category = True
            obj.save()
        except:
            obj = CommunityCategory(community_id=community, category_id=category, community_category=True)
            self.check_object_permissions(self.request, obj)
            obj.save()

        serializer = CommunityCategorySerializer(obj, context={'request': request})

        return Response(serializer.data)


class DeleteCommunityCategoryView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)

    serializer_class = CommunityCategorySerializer

    def get_object(self):
        community = self.kwargs['community']
        category = self.kwargs['category']
        object = CommunityCategory.objects.get(community=community, category=category)
        self.check_object_permissions(self.request, object)
        return object


class CommunitiesByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CommunitySerializer

    def get_queryset(self):

        page = int(self.kwargs['page'])
        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        company = self.request.GET.get('company', None)
        user = self.request.GET.get('user', None)
        keyword = self.request.GET.get('keyword', None)
        tag = self.request.GET.get('tag', None)
        ordering = self.request.GET.get('ordering', None)

        # if keyword is not None:
        #
        #     s = CommunityDocument.search()
        #     filter_list = Qel("multi_match", query=keyword, fields=['name',
        #                                                             'description',
        #
        #                                                             'tags'
        #
        #                                                             ])
        #
        #     filter_list = filter_list & Qel('match', deleted=False)
        #     if country is not None:
        #         filter_list = filter_list & Qel('match', country=country)
        #     if city is not None:
        #         filter_list = filter_list & Qel('match', city=city)
        #     if region is not None:
        #         filter_list = filter_list & Qel('match', region=region)
        #
        #
        #     if category is not None:
        #         filter_list = filter_list & Qel('match', categories=category)
        #
        #     ordering_code = get_elastic_ordering(ordering)
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
        #     ids = [hit['_id'] for hit in hits]
        #     ordering_code = get_ordering(ordering)
        #     objects = Community.objects.language().fallbacks('en').filter(id__in=ids).order_by(*ordering_code)

        # else:
        filter_list = Q(deleted=False)

        if keyword is not None:
            filter_list &= Q(name__icontains=keyword) | Q(description__icontains=keyword)

        if category is not None:
            filter_list = filter_list & Q(categories__category=category)
        if country is not None:
            filter_list = filter_list & Q(country=country)
        if city is not None:
            filter_list = filter_list & Q(city=city)
        if region is not None:
            filter_list = filter_list & Q(city__region=region)
        if company is not None:
            filter_list = filter_list & Q(companies__company=company)
        if user is not None:
            filter_list = filter_list & Q(members__user=user)
        if keyword is not None:
            filter_list = filter_list & Q(name__icontains=keyword)
        if tag is not None:
            tag = tag.lower()
            filter_list = filter_list & Q(tags__name__in=[tag])

        ordering_code = get_ordering(ordering)

        if page == 0:
            objects = Community.objects.language().fallbacks('en').filter(filter_list).order_by(*ordering_code)[:10]

        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = Community.objects.language().fallbacks('en').filter(filter_list).order_by(*ordering_code)[
                      item_from:item_to]

        return objects


class CommunitiesCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):

        category = self.request.GET.get('category', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        company = self.request.GET.get('company', None)
        user = self.request.GET.get('user', None)
        keyword = self.request.GET.get('keyword', None)

        filter_list = Q(deleted=False)

        if category is not None:
            filter_list = filter_list & Q(categories__category=category)
        if country is not None:
            filter_list = filter_list & Q(country=country)
        if city is not None:
            filter_list = filter_list & Q(city=city)
        if region is not None:
            filter_list = filter_list & Q(city__region=region)
        if company is not None:
            filter_list = filter_list & Q(companies__company=company)
        if user is not None:
            filter_list = filter_list & Q(members__user=user)
        if keyword is not None:
            filter_list = filter_list & Q(name__icontains=keyword)

        count = Community.objects.language().fallbacks('en').filter(filter_list).count()

        data = {'count': count}

        return Response(data)


class CommunityDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Community.objects.language().fallbacks('en').filter(deleted=False)
    serializer_class = CommunitySerializer


class CommunityDetailsInLanguageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CommunitySerializer

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        object = Community.objects.language(language).fallbacks('en').get(pk=pk, deleted=False)
        return object


class CommunitiesByNameView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CommunitySerializer

    def get_queryset(self):
        name = self.kwargs['name']
        return Community.objects.language('all').filter(name__icontains=name, deleted=False)


class UpdateCommunityDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdmin)

    serializer_class = CommunitySerializer

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        object = Community.objects.language(language).fallbacks('en').get(pk=pk, deleted=False)
        self.check_object_permissions(self.request, object)
        return object


class CreateCommunityView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = CommunitySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            community_user = CommunityMember(community_id=serializer.data['id'], user=request.user, admin=True)

            community_user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityMembersView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommunityMemberSerializer

    def get_queryset(self):
        community = self.kwargs['community']
        page = int(self.kwargs['page'])

        if page == 0:
            objects = CommunityMember.objects.filter(community=community)[:10]

        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = CommunityMember.objects.filter(community=community)[item_from:item_to]
        return objects


class CommunityMembersCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, community):
        count = CommunityMember.objects.filter(community=community).count()
        data = {'count': count}

        return Response(data)


class CreateCommunityMemberView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOpenCommunityOrAdmin)
    serializer_class = CommunityMemberSerializer
    queryset = CommunityMember.objects.all()


class LeaveCommunityView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsUserOrAdmin)
    serializer_class = CommunityMemberSerializer
    queryset = CommunityMember.objects.all()


class LeaveCompanyCommunityView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsCompanyAdminOrCommunityAdmin)
    serializer_class = CommunityCompanySerializer
    queryset = CommunityCompany.objects.all()


class MemberPermisionsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommunityMemberSerializer

    def get_object(self):
        user = self.kwargs['user']
        community = self.kwargs['community']
        try:
            object = CommunityMember.objects.get(community=community, user=user)
        except:
            object = None
        return object


# class CommunityMemberUpdateView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
#     serializer_class = CommunityMemberSerializer
#     queryset = CommunityMember.objects.all()


class DeleteCommunityMemberView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsUserOrAdmin)

    serializer_class = CommunityMemberSerializer

    def get_object(self):
        community = self.kwargs['community']
        user = self.kwargs['user']
        object = CommunityMember.objects.get(community=community, user=user)
        self.check_object_permissions(self.request, object)
        return object


class DeleteCommunityCompanyView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsCompanyAdminOrCommunityAdmin)

    serializer_class = CommunityCompanySerializer

    def get_object(self):
        community = self.kwargs['community']
        company = self.kwargs['company']
        object = CommunityCompany.objects.get(community=community, company=company)
        self.check_object_permissions(self.request, object)
        return object


class CommunityCompaniesView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommunityCompanySerializer

    def get_queryset(self):
        community = self.kwargs['community']
        page = int(self.kwargs['page'])

        if page == 0:
            objects = CommunityCompany.objects.filter(community=community)[:10]

        else:

            item_from = page * 10
            item_to = page * 10 + 10
            objects = CommunityCompany.objects.filter(community=community)[item_from:item_to]
        return objects


class CommunityCompaniesCountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, community):
        count = CommunityCompany.objects.filter(community=community).count()
        data = {'count': count}

        return Response(data)


class CreateCommunityCompanyView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
    serializer_class = CommunityCompanySerializer
    queryset = CommunityCompany.objects.all()


class CommunityCompanyUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
    serializer_class = CommunityCompanySerializer
    queryset = CommunityCompany.objects.all()


class GetCommunityCompanyView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsCompanyAdminOrCommunityAdmin)

    serializer_class = CommunityCompanySerializer

    def get_object(self):
        company = self.kwargs['company']
        community = self.kwargs['community']
        object = CommunityCompany.objects.get(community=community, company=company)
        self.check_object_permissions(self.request, object)
        return object


class UserAcceptCommunityInvitationView(APIView):
    permission_classes = (IsAuthenticated, IsInvitationUser)

    def put(self, request, *args, **kwargs):
        id = request.data['id']
        accepted_by_user = request.data['accepted_by_user']

        object = CommunityInvitation.objects.get(id=id)

        self.check_object_permissions(self.request, object)
        object.accepted_by_user = accepted_by_user
        object.pending = False
        object.save()

        serializer = CommunityInvitationSerializer(object, context={'request': request})

        return Response(serializer.data)


class AdminCreateCommunityInvitationView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
    serializer_class = CommunityInvitationSerializer
    queryset = CommunityInvitation.objects.all()


class UserCreateCommunityInvitationView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        community = request.data['community']
        company = request.data['company']
        accepted_by_user = request.data['accepted_by_user']
        message = request.data['message']

        obj = CommunityInvitation(community_id=community, user=request.user, accepted_by_user=accepted_by_user,
                                  company_id=company,
                                  message=message, pending=True)
        obj.save()
        serializer = CommunityInvitationSerializer(obj, context={'request': request})

        return Response(serializer.data)


class UserCompaniesInCommunityInvitationsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CommunityInvitationSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        community = self.kwargs['community']
        queryset = CommunityInvitation.objects.filter(user=user, community=community, company__isnull=False,
                                                      user_acceptance=False, accepted_by_user=True)
        return queryset


class DeleteCommunityInvitationView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsUserOrAdmin)
    serializer_class = CommunityInvitationSerializer
    queryset = CommunityInvitation.objects.all()


class DeleteCommunityInvitationByUserView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsUserOrAdmin)
    serializer_class = CommunityInvitationSerializer

    def get_object(self):
        community = self.kwargs['community']
        user = self.kwargs['user']
        obj = CommunityInvitation.objects.get(community=community, user=user)
        self.check_object_permissions(self.request, obj)

        return obj


class CommunityInvitationUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
    serializer_class = CommunityInvitationSerializer
    queryset = CommunityInvitation.objects.all()


class CommunityInvitationsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
    serializer_class = CommunityInvitationSerializer

    def get_queryset(self):
        community = self.kwargs['community']
        queryset = CommunityInvitation.objects.filter(community=community, pending=True)
        return queryset


class GetInvitationForMemberView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommunityInvitationSerializer

    def get_object(self):
        user = self.kwargs['user']
        community = self.kwargs['community']

        try:
            object = CommunityInvitation.objects.get(community=community, user=user, company__isnull=True)
        except:
            object = None
        return object


class GetInvitationForCompanyView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommunityInvitationSerializer

    def get_object(self):

        community = self.kwargs['community']
        company = self.kwargs['company']
        try:
            object = CommunityInvitation.objects.get(community=community, company=company)
        except:
            object = None
        return object


class SetCommunityAdminStatusView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCommunityAdminDetails)
    serializer_class = CommunityMemberSerializer

    def put(self, request, *args, **kwargs):

        value = int(request.data['value'])
        community = self.kwargs['community']
        user = self.kwargs['user']

        if value == 1:
            admin_status = True
        else:
            admin_status = False

        try:
            obj = CommunityMember.objects.get(community=community, user=user)
        except CommunityMember.DoesNotExist:
            return status.HTTP_404_NOT_FOUND

        self.check_object_permissions(self.request, obj)
        obj.admin = admin_status

        obj.save()

        return Response({'value': admin_status})


class CheckDeleteCommunityAdminStatusView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        user = request.user

        communities = CommunityMember.objects.filter(user=user, community__deleted=False, admin=True)

        for community in communities.all():
            count = CommunityMember.objects.filter(community=community.community, user__is_active=True).exclude(
                user=user).count()
            if not count:
                translation = get_translation(community.community, 'en')
                return Response({'status': False, 'community': translation.name})
        return Response({'status': True})
