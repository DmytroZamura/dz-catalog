from __future__ import unicode_literals
from __future__ import absolute_import
from django.contrib import admin
from hvad.admin import TranslatableAdmin
from .models import CompanyType, Company, CompanySize, CompanyUser, CompanyIndustry, CompanyCategory, CompanyFollower, \
    CompanyEventsQty, FavoriteCompany, CompanySEOData, IndustryClassification


class CompanyIndustryAdmin(TranslatableAdmin):
    change_list_template = 'smuggler/change_list.html'
    list_display = [field.name for field in CompanyIndustry._meta.fields]

    class Meta:
        model = CompanyIndustry


admin.site.register(CompanyIndustry, CompanyIndustryAdmin)


class IndustryClassificationAdmin(admin.ModelAdmin):
    change_list_template = 'smuggler/change_list.html'
    list_display = [field.name for field in IndustryClassification._meta.fields]
    search_fields = ['slug', 'name_en', 'name_ru']

    class Meta:
        model = IndustryClassification


admin.site.register(IndustryClassification, IndustryClassificationAdmin)


class CompanyTypeAdmin(TranslatableAdmin):
    list_display = [field.name for field in CompanyType._meta.fields]

    class Meta:
        model = CompanyType


admin.site.register(CompanyType, CompanyTypeAdmin)


class CompanyAdmin(TranslatableAdmin):
    # list_select_related = ('origin', 'unit_type', 'currency')
    list_display = ['id', 'slug']
    raw_id_fields = ('country', 'city',)
    search_fields = ['slug']

    # list_display = [field.name for field in Product._meta.fields]

    class Meta:
        model = Company


admin.site.register(Company, CompanyAdmin)


class CompanySEODataAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanySEOData._meta.fields]

    class Meta:
        model = CompanySEOData


admin.site.register(CompanySEOData, CompanySEODataAdmin)


class CompanyEventsQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyEventsQty._meta.fields]

    class Meta:
        model = CompanyEventsQty


admin.site.register(CompanyEventsQty, CompanyEventsQtyAdmin)


class CompanySizeAdmin(TranslatableAdmin):
    list_display = [field.name for field in CompanySize._meta.fields]

    class Meta:
        model = CompanySize


admin.site.register(CompanySize, CompanySizeAdmin)


class CompanyUserAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyUser._meta.fields]

    class Meta:
        model = CompanyUser


admin.site.register(CompanyUser, CompanyUserAdmin)


class CompanyCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyCategory._meta.fields]

    class Meta:
        model = CompanyCategory


admin.site.register(CompanyCategory, CompanyCategoryAdmin)


class CompanyFollowerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CompanyFollower._meta.fields]

    class Meta:
        model = CompanyFollower


admin.site.register(CompanyFollower, CompanyFollowerAdmin)


class FavoriteCompanyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FavoriteCompany._meta.fields]

    class Meta:
        model = FavoriteCompany


admin.site.register(FavoriteCompany, FavoriteCompanyAdmin)
