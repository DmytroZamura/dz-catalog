from __future__ import absolute_import
from django.contrib import admin
from django import forms
from .models import *
from hvad.admin import TranslatableAdmin, TranslatableModelForm
from catalog.attribute.models import Attribute


# class CategoryAdminForm(TranslatableModelForm):
#     def __init__(self, *args, **kwargs):
#         super(CategoryAdminForm, self).__init__(*args, **kwargs)
#         self.fields['parent'].queryset = Category.objects.language().all()
#
#         self.fields['parent'].label_from_instance = lambda obj: obj.default_name


class CategoryAdmin(TranslatableAdmin):

    list_display = ['pk', 'slug', 'default_name', 'external_code', 'full_name', 'child_qty', 'approved']
    search_fields = ['default_name', 'external_code', 'pk']
    raw_id_fields = ('parent',)

    class Meta:
        model = Category


admin.site.register(Category, CategoryAdmin)


class CategoryAttributeAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CategoryAttributeAdminForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.language().all()
        self.fields['category'].label_from_instance = lambda obj: obj.default_name
        self.fields['attribute'].queryset = Attribute.objects.language().all()
        self.fields['attribute'].label_from_instance = lambda obj: obj.name


class CategoryAttributeAdmin(admin.ModelAdmin):
    form = CategoryAttributeAdminForm
    list_display = ['pk', 'category_name', 'attribute_name', 'position', 'default_attribute']

    class Meta:
        model = CategoryAttribute


admin.site.register(CategoryAttribute, CategoryAttributeAdmin)





class SuggestedCategoryAdmin(admin.ModelAdmin):



    list_display = [field.name for field in SuggestedCategory._meta.fields]
    raw_id_fields = ('category',)

    class Meta:
        model = SuggestedCategory


admin.site.register(SuggestedCategory, SuggestedCategoryAdmin)


class CategoryNameAdmin(admin.ModelAdmin):
    change_list_template = 'smuggler/change_list.html'
    list_display = [field.name for field in CategoryName._meta.fields]
    search_fields = ['code', 'name']

    class Meta:
        model = CategoryName


admin.site.register(CategoryName, CategoryNameAdmin)


class CategoryClassificationAdmin(admin.ModelAdmin):
    change_list_template = 'smuggler/change_list.html'
    list_display = [field.name for field in CategoryClassification._meta.fields]
    search_fields = ['level1_code', 'level2_code', 'level3_code', 'level4_code', 'level5_code', 'level6_code',
                     'level1_ru_name', 'level2_ru_name', 'level3_ru_name', 'level4_ru_name', 'level5_ru_name',
                     'level6_ru_name',
                     'level1_en_name', 'level2_en_name', 'level3_en_name', 'level4_en_name', 'level5_en_name',
                     'level6_en_name']

    class Meta:
        model = CategoryClassification


admin.site.register(CategoryClassification, CategoryClassificationAdmin)
