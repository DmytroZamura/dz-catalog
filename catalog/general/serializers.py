from rest_framework import serializers
from hvad.contrib.restframework.serializers import TranslatableModelSerializer
from .models import Country, Language, UnitType, Currency, City, JobFunction, JobType, SeniorityLabel, Region, \
    Translation


class CurrencySerializer(TranslatableModelSerializer):
    class Meta:
        model = Currency
        fields = ('id', 'code', 'name')


class CountrySerializer(TranslatableModelSerializer):
    currency_details = CurrencySerializer(source='currency', required=False, read_only=True)
    flag_url = serializers.SerializerMethodField()

    def get_flag_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.flag_url)
        else:
            return None

    class Meta:
        model = Country
        fields = ('id', 'name', 'code', 'short_name', 'flag', 'flag_url', 'currency', 'currency_details', 'slug')

class CountrySmallSerializer(TranslatableModelSerializer):

    flag_url = serializers.SerializerMethodField()

    def get_flag_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.flag_url)
        else:
            return None

    class Meta:
        model = Country
        fields = ('id', 'name', 'code', 'short_name', 'flag', 'flag_url', 'currency', 'slug')


class RegionSerializer(TranslatableModelSerializer):
    country_details = CountrySerializer(source='country', required=False, read_only=True)

    class Meta:
        model = Region
        fields = ('id', 'country', 'country_details', 'name', 'slug')


class CitySerializer(TranslatableModelSerializer):
    country_details = CountrySerializer(source='country', required=False, read_only=True)
    region_details = RegionSerializer(source='region', required=False, read_only=True)
    emblem_url = serializers.SerializerMethodField()
    head_photo_url = serializers.SerializerMethodField()

    def get_emblem_url(self, obj):
        if self.context:
            return self.context['request'].build_absolute_uri(obj.emblem_url)
        else:
            return None

    def get_head_photo_url(self, obj):

        if self.context:
            return self.context['request'].build_absolute_uri(obj.head_photo_url)
        else:
            return None

    class Meta:
        model = City
        fields = (
            'id', 'country', 'country_details', 'region', 'region_details', 'name', 'emblem', 'emblem_url',
            'head_photo',
            'head_photo_url', 'slug')

class CitySmallSerializer(TranslatableModelSerializer):


    class Meta:
        model = City
        fields = (
            'id', 'country', 'region',  'name', 'slug')


class LanguageSerializer(TranslatableModelSerializer):
    class Meta:
        model = Language
        fields = ('id', 'code', 'name')


class JobTypeSerializer(TranslatableModelSerializer):
    class Meta:
        model = JobType
        fields = ('id', 'name', 'slug')


class JobFunctionSerializer(TranslatableModelSerializer):
    class Meta:
        model = JobFunction
        fields = ('id', 'name', 'slug')


class SeniorityLabelSerializer(TranslatableModelSerializer):
    class Meta:
        model = SeniorityLabel
        fields = ('id', 'name', 'slug')


class UnitTypeSerializer(TranslatableModelSerializer):
    class Meta:
        model = UnitType
        fields = ('id', 'code', 'name', 'name_plural')


class TranslationSerializer(TranslatableModelSerializer):
    class Meta:
        model = Translation
        fields = ('id', 'code', 'text')
