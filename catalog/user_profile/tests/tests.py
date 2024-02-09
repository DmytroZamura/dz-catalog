from catalog.user_profile.models import UserProfile
from catalog.utils.cases_for_tests import BaseTestCaseMixin
from django.test import TestCase


# Create your tests here.
class ProfileTestCase(BaseTestCaseMixin, TestCase):

    def test_profiles_created(self):
        count = UserProfile.objects.language('en').count()
        self.assertEqual(count, 2)
