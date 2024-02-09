from __future__ import unicode_literals
from __future__ import absolute_import
from django.contrib import admin
from django import forms
from hvad.admin import TranslatableAdmin, TranslatableModelForm
from .models import Country, Language, UnitType, Currency, City, CurrencyRate, JobFunction, JobType, SeniorityLabel, \
    Translation, Region, UnitTypeClassification


class CountryAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(CountryAdminForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.language().all().order_by('default_name')

        self.fields['currency'].label_from_instance = lambda obj: obj.name

class CountryAdmin(TranslatableAdmin):
    form = CountryAdminForm
    list_display = ['id', 'default_name', 'slug', 'geoname_id', 'code', 'code2',  'tld']
    search_fields = ['default_name', 'code', 'code2',  'tld']

    class Meta:
        model = Country


admin.site.register(Country, CountryAdmin)

class RegionAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(RegionAdminForm, self).__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.language().all()

        self.fields['country'].label_from_instance = lambda obj: obj.default_name

class RegionAdmin(TranslatableAdmin):
    form = RegionAdminForm
    list_display = ['default_name', 'slug', 'geoname_id']
    search_fields = ['default_name', 'slug', 'geoname_id']

    class Meta:
        model = Region


admin.site.register(Region, RegionAdmin)




class CityAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(CityAdminForm, self).__init__(*args, **kwargs)

        # self.fields['country'].queryset = Country.objects.language('en').all()
        # self.fields['country'].label_from_instance = lambda obj: obj.name
        # self.fields['region'].queryset = Region.objects.language('en').all()
        # self.fields['region'].label_from_instance = lambda obj: obj.name


class CityAdmin(TranslatableAdmin):
    # form = CityAdminForm
    list_display = ['id', 'default_name', 'geoname_id', 'slug', 'posts_exist', 'users_exist', 'companies_exist', 'products_exist', 'communities_exist']
    search_fields = ['default_name', 'slug', 'geoname_id']
    raw_id_fields = ('country', 'region',)
    class Meta:
        model = City


admin.site.register(City, CityAdmin)


class LanguageAdmin(TranslatableAdmin):
    list_display = [field.name for field in Language._meta.fields]

    class Meta:
        model = Language


admin.site.register(Language, LanguageAdmin)


class UnitTypeAdmin(TranslatableAdmin):
    list_display = ['id', 'default_name']
    search_fields = ['default_name']


    class Meta:
        model = UnitType


admin.site.register(UnitType, UnitTypeAdmin)


class UnitTypeClassificationAdmin(admin.ModelAdmin):
    change_list_template = 'smuggler/change_list.html'
    list_display = [field.name for field in UnitTypeClassification._meta.fields]
    search_fields = ['name_en', 'name_ru', 'name_uk']

    class Meta:
        model = UnitTypeClassification
admin.site.register(UnitTypeClassification, UnitTypeClassificationAdmin)


class CurrencyAdmin(TranslatableAdmin):
    list_display = [field.name for field in Currency._meta.fields]
    search_fields = ['code', 'number', 'default_name']

    class Meta:
        model = Currency


admin.site.register(Currency, CurrencyAdmin)


class CurrencyRateAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CurrencyRateAdminForm, self).__init__(*args, **kwargs)
        self.fields['currency'].queryset = Currency.objects.language('en').all()
        self.fields['currency'].label_from_instance = lambda obj: obj.code
        self.fields['currency_to'].queryset = Currency.objects.language('en').all()
        self.fields['currency_to'].label_from_instance = lambda obj: obj.code


class CurrencyRateAdmin(admin.ModelAdmin):
    form = CurrencyRateAdminForm
    list_display = ['pk', 'currency_code', 'currency_to_code', 'rate', 'update_date']

    class Meta:
        model = CurrencyRate


admin.site.register(CurrencyRate, CurrencyRateAdmin)


class JobTypeAdmin(TranslatableAdmin):
    list_display = ['pk', 'default_name', 'position']

    class Meta:
        model = JobType


admin.site.register(JobType, JobTypeAdmin)


class JobFunctionAdmin(TranslatableAdmin):
    list_display = ['pk', 'default_name', 'position']

    class Meta:
        model = JobFunction


admin.site.register(JobFunction, JobFunctionAdmin)


class SeniorityLabelAdmin(TranslatableAdmin):
    list_display = ['pk', 'default_name', 'position']

    class Meta:
        model = SeniorityLabel


admin.site.register(SeniorityLabel, SeniorityLabelAdmin)


class TranslationAdmin(TranslatableAdmin):
    list_display = [field.name for field in Translation._meta.fields]

    class Meta:
        model = Translation

admin.site.register(Translation, TranslationAdmin)
