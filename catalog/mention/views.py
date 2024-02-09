from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from catalog.company.models import Company
from catalog.company.serializers import CompanyShortSerializer
from catalog.user_profile.models import UserProfile
from catalog.user_profile.serializers import UserProfileShortSerializer
from django.db.models import Q
from sorl.thumbnail import get_thumbnail


class MentionView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, slug):
        company_details = None
        profile_details = None

        try:
            company = Company.objects.language().fallbacks('en').get(slug__iexact=slug, deleted=False)
            company_details = CompanyShortSerializer(company, context={'request': request}).data
        except Company.DoesNotExist:
            try:
                profile = UserProfile.objects.language().fallbacks('en').get(slug__iexact=slug, deleted=False)
                profile_details = UserProfileShortSerializer(profile, context={'request': request}).data
            except UserProfile.DoesNotExist:
                pass
        data = {
            'company_details': company_details,
            'profile_details': profile_details
        }
        return Response(data)


class SearchMentionsByName(APIView):
    def get(self, request, name):

        filter_list = (Q(name__icontains=name) | Q(slug__icontains=name)) & Q(deleted=False)

        results = Company.objects.language().filter(filter_list).distinct().order_by('name')[:10]

        if not results:
            results = Company.objects.language('en').filter(filter_list).distinct().order_by('name')[:10]

        filter_list = (Q(user__following_profiles__profile=request.user.user_profile) | Q(
            followers__user=request.user))
        filter_name = (Q(full_name__icontains=name) | Q(slug__icontains=name)) & Q(deleted=False)

        filter_list = filter_list & filter_name

        user_results = UserProfile.objects.language().filter(filter_list).order_by('first_name', 'last_name').distinct()[:10]

        if not user_results:
            user_results = UserProfile.objects.language('en').filter(filter_list).order_by('first_name', 'last_name').distinct()[:10]

        if not user_results:
            user_results = UserProfile.objects.language().filter(filter_name).order_by('first_name', 'last_name').distinct()[:10]
        if not user_results:
            user_results = UserProfile.objects.language('en').filter(filter_name).order_by('first_name', 'last_name').distinct()[:10]

        data = []

        for item in user_results:
            image = ''
            if item.img:
                image = get_thumbnail(item.img.file, '80x80', crop='center', quality=99).url
            if item.last_name:
                user_name = "%s %s" % (item.first_name, item.last_name)
            else:
                user_name = item.first_name
            data_object = {

                'id': item.user_id,
                'name': user_name,
                'slug': item.slug,
                'image': image,
                'type': 'user'
            }
            data.append(data_object)

        for item in results:
            image = ''
            if item.logo:
                image = get_thumbnail(item.logo.file, '80x80', crop='center', quality=99).url

            data_object = {
                'id': item.id,
                'name': item.name,
                'slug': item.slug,
                'image': image,
                'type': 'company'
            }

            data.append(data_object)

        return Response(data)
