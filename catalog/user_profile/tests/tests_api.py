from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from catalog.utils.cases_for_tests import BaseTestCaseMixin
from django.conf.urls import include, url
from catalog.user_profile.models import UserProfile, UserProfileFollower
from catalog.user_profile.views import FollowUserProfileView
from django.contrib.auth.models import User


class AccountTests(BaseTestCaseMixin, APITestCase):
    urlpatterns = [
        url(r'api/', include('catalog.user_profile.urls')),
    ]

    def test_profile_details_exists(self):
        """
        Ensure user profile created.
        """
        api_url = reverse('get-profile', kwargs={'user': 1})
        response = self.client.get(api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user_id'], 1)

    def test_user_follow_user_profile(self):
        """
        Ensure user can follow profile of another user.
        """
        factory = APIRequestFactory()
        view = FollowUserProfileView.as_view()
        user = User.objects.get(id=1)
        profile = UserProfile.objects.language('en').get(user_id=2)
        data = {'user': user.id, 'profile': profile.id}
        api_url = reverse('follow-profile')
        request = factory.post(api_url, data)
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        follow_record = UserProfileFollower.objects.get(user=user, profile=profile)
        self.assertEqual(follow_record.user, user)

        #Ensure that events_qty changed
        self.assertEqual(profile.eventsqty.followers, 1)
        self.assertEqual(user.user_profile.eventsqty.following, 1)

