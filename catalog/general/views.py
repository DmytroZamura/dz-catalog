from __future__ import unicode_literals
from rest_framework.permissions import AllowAny
from .serializers import CountrySerializer, LanguageSerializer, UnitTypeSerializer, CurrencySerializer, CitySerializer, \
    JobFunctionSerializer, JobTypeSerializer, SeniorityLabelSerializer, RegionSerializer, TranslationSerializer
from .models import Country, Language, UnitType, Currency, City, JobType, JobFunction, SeniorityLabel, Region, \
    Translation
from rest_framework import generics
from .documents import CityDocument
from django.db.models import Q
from rest_framework.views import APIView
from django.conf import settings
from catalog.general.models import CurrencyRate
from datetime import datetime
import requests
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist


class CountriesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CountrySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CountriesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.request.GET.get('name', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)

        filter_list = Q()

        if name is not None:
            filter_list = filter_list & Q(name__icontains=name)
        if posts_exist is not None:
            filter_list = filter_list & Q(posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(communities_exist=True)
        objects = Country.objects.language().fallbacks('en').filter(filter_list).order_by('name')
        if not objects and name:
            objects = Country.objects.language('en').filter(filter_list).order_by('name')

        return objects


class ExistedCountriesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CountrySerializer

    @method_decorator(cache_page(60 * 10))
    def dispatch(self, *args, **kwargs):
        return super(ExistedCountriesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.request.GET.get('name', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)

        filter_list = Q()

        if name is not None:
            filter_list = filter_list & Q(name__icontains=name)
        if posts_exist is not None:
            filter_list = filter_list & Q(posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(communities_exist=True)
        objects = Country.objects.language().fallbacks('en').filter(filter_list).order_by('name')
        if not objects and name:
            objects = Country.objects.language('en').filter(filter_list).order_by('name')

        return objects


class RegionsListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegionSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(RegionsListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        country = self.request.GET.get('country', None)
        name = self.request.GET.get('name', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)
        filter_list = Q()

        if country is not None:
            filter_list = filter_list & Q(country=country)
        if name is not None:
            filter_list = filter_list & Q(name__icontains=name)
        if posts_exist is not None:
            filter_list = filter_list & Q(region_cities__posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(region_cities__companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(region_cities__products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(region_cities__users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(region_cities__communities_exist=True)

        objects = Region.objects.language().fallbacks('en').filter(filter_list).distinct().order_by('name')
        if not objects and name:
            objects = Region.objects.language('en').filter(filter_list).distinct().order_by('name')

        return objects


class ExistedRegionsListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegionSerializer

    @method_decorator(cache_page(60 * 10))
    def dispatch(self, *args, **kwargs):
        return super(ExistedRegionsListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        country = self.request.GET.get('country', None)
        name = self.request.GET.get('name', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)
        filter_list = Q()

        if country is not None:
            filter_list = filter_list & Q(country=country)
        if name is not None:
            filter_list = filter_list & Q(name__icontains=name)
        if posts_exist is not None:
            filter_list = filter_list & Q(region_cities__posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(region_cities__companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(region_cities__products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(region_cities__users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(region_cities__communities_exist=True)
        objects = Region.objects.language().fallbacks('en').filter(filter_list).distinct().order_by('name')
        if not objects and name:
            objects = Region.objects.language('en').filter(filter_list).distinct().order_by('name')

        return objects


class CitiesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CitiesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.request.GET.get('name', None)
        country = self.request.GET.get('country', None)
        region = self.request.GET.get('region', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)
        filter_list = Q()

        if country is not None:
            filter_list = filter_list & Q(country=country)
        if region is not None:
            filter_list = filter_list & Q(region=region)
        if posts_exist is not None:
            filter_list = filter_list & Q(posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(communities_exist=True)
        if name is not None:
            filter_list = filter_list & Q(name__icontains=name)

        if country:
            objects = City.objects.language().fallbacks('en').filter(filter_list).order_by('name')[:200]
            if not objects and name:
                objects = City.objects.language('en').filter(filter_list).order_by('name')[:200]
        else:
            objects = City.objects.language().fallbacks('en').filter(filter_list).order_by('name')[:100]
            if not objects and name:
                objects = City.objects.language('en').filter(filter_list).order_by('name')[:100]

        return objects


class ExistedCitiesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 10))
    def dispatch(self, *args, **kwargs):
        return super(ExistedCitiesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.request.GET.get('name', None)
        country = self.request.GET.get('country', None)
        region = self.request.GET.get('region', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)
        filter_list = Q()

        if country is not None:
            filter_list = filter_list & Q(country=country)
        if region is not None:
            filter_list = filter_list & Q(region=region)
        if posts_exist is not None:
            filter_list = filter_list & Q(posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(communities_exist=True)
        if name is not None:
            filter_list = filter_list & Q(name__icontains=name)

        objects = City.objects.language().fallbacks('en').filter(filter_list).order_by('name')
        if not objects and name:
            objects = City.objects.language('en').filter(filter_list).order_by('name')

        return objects


class CountryDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Country.objects.language().fallbacks('en').all()
    serializer_class = CountrySerializer


class CountrySearchView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CountrySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CountrySearchView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.kwargs['name']
        objects = Country.objects.language().filter(name__icontains=name).order_by('name')
        if not objects:
            objects = Country.objects.language('en').filter(name__icontains=name).order_by('name')

        return objects


class CitiesOfCountryListView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CitiesOfCountryListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        country = self.kwargs['country']
        queryset = City.objects.language().fallbacks('en').filter(country=country).order_by('name')

        return queryset


class CityDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = City.objects.language().fallbacks('en').all()
    serializer_class = CitySerializer


class CityByNameView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CityByNameView, self).dispatch(*args, **kwargs)

    def get_object(self):
        name = self.kwargs['name']
        country = self.kwargs['country']

        obj = City.objects.language().filter(country=country, name=name).first()
        if not obj:
            obj = City.objects.language('en').filter(country=country, name=name).first()

        return obj


class TranslationView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TranslationSerializer

    @method_decorator(cache_page(60 * 60 * 5))
    def dispatch(self, *args, **kwargs):
        return super(TranslationView, self).dispatch(*args, **kwargs)

    def get_object(self):
        code = self.kwargs['code']
        obj = Translation.objects.language().fallbacks('en').get(code=code)
        return obj


class CityOfCountrySearchView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CityOfCountrySearchView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.kwargs['name']
        country = self.kwargs['country']

        objects = City.objects.language().filter(country=country, name__icontains=name).order_by('name')
        if not objects:
            objects = City.objects.language('en').filter(country=country, name__icontains=name).order_by('name')

        return objects


class CitySearchView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CitySearchView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.kwargs['name']

        objects = City.objects.language().filter(name__icontains=name).order_by('name')
        if not objects:
            objects = City.objects.language('en').filter(name__icontains=name).order_by('name')

        return objects


class LanguageSearchView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LanguageSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(LanguageSearchView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.kwargs['name']
        objects = Language.objects.language().filter(name__icontains=name).order_by('name')
        if not objects:
            objects = Language.objects.language('en').filter(name__icontains=name).order_by('name')

        return objects


class GeoCitySearchView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CitySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(GeoCitySearchView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        lat = self.kwargs['lat']
        lon = self.kwargs['lon']

        if lat != 'null' and lon != 'null':
            s = CityDocument.search()

            s = s.filter(
                'geo_distance', distance='50km', location={"lat": lat, "lon": lon}
            ).sort({'_geo_distance': {
                'location': {'lat': lat, 'lon': lon},
                "order": "asc",
                "unit": "km",
                "distance_type": "arc"
            }})[:1]

            try:
                response = s.execute()
                response_dict = response.to_dict()
                hits = response_dict['hits']['hits']
                ids = [hit['_id'] for hit in hits]
                objects = City.objects.language().fallbacks('en').filter(id__in=ids)
            except ObjectDoesNotExist:
                objects = None
        else:
            objects = None

        return objects


class LanguageDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class LanguageDetailsByCodeView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def get_object(self):
        code = self.kwargs['code']
        object = Language.objects.language().get(code=code)
        return object


class LanguagesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LanguageSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(LanguagesListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = Language.objects.language().filter(locale_lang=True).order_by('name')
        return queryset


class UnitTypesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UnitTypeSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(UnitTypesListView, self).dispatch(*args, **kwargs)

    queryset = UnitType.objects.language().all().order_by('code')


class CurrenciesListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CurrencySerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(CurrenciesListView, self).dispatch(*args, **kwargs)

    queryset = Currency.objects.all().order_by('code')


class CurrencyDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Currency.objects.language().fallbacks('en').all()
    serializer_class = CurrencySerializer


class JobTypeListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = JobTypeSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(JobTypeListView, self).dispatch(*args, **kwargs)

    queryset = JobType.objects.language().all()


class JobFunctionListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = JobFunctionSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(JobFunctionListView, self).dispatch(*args, **kwargs)

    queryset = JobFunction.objects.language().all()


class SeniorityLabelListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SeniorityLabelSerializer

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super(SeniorityLabelListView, self).dispatch(*args, **kwargs)

    queryset = SeniorityLabel.objects.language().all()


def refreshRates():
    current_rate = CurrencyRate.objects.first()
    if current_rate.update_date.date() != datetime.now().date():

        url = 'https://data.fixer.io/api/latest?access_key=' + settings.FIXER_KEY + '&base=USD'

        response = requests.get(url).json()
        currensies = Currency.objects.language('en').all()
        rates = response['rates']
        for curr in currensies:

            # print(curr.default_name)

            rate = 0
            try:
                rate = rates[curr.code]
            except:
                print(curr.default_name + ' - no rate')

            if rate != 0:
                try:
                    cur_rate = CurrencyRate.objects.get(currency__code=curr.code, currency_to__code='USD')
                    cur_rate.rate = rate
                    cur_rate.save()
                except CurrencyRate.DoesNotExist:
                    CurrencyRate.objects.create(currency=curr, currency_to_id=1,
                                                rate=rate)


class RefreshRatesView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refreshRates()

        return Response(True)
