from .models import UserProfileEmployment
from hvad.contrib.restframework.serializers import TranslatableModelSerializer

from catalog.company.serializers import CompanyShortSerializer
from catalog.general.serializers import CountrySerializer, CitySerializer


class UserProfileEmploymentSerializer(TranslatableModelSerializer):
    company_details = CompanyShortSerializer(source='company', required=False, read_only=True)
    company_default_details = CompanyShortSerializer(source='company', required=False, read_only=True, language='en')
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    city_details = CitySerializer(source='city', required=False, read_only=True)

    class Meta:
        model = UserProfileEmployment
        fields = ('id', 'profile', 'company', 'company_details', 'company_default_details', 'company_name', 'title',
                  'description', 'country', 'country_details', 'city', 'city_details', 'city_name', 'start_date',
                  'end_date', 'present_time', 'education',
                                              'position', 'language_code')
