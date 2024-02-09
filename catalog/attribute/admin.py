from __future__ import absolute_import
from django.contrib import admin
from .models import Attribute, AttributeValue, AttributeClassification
from catalog.general.models import UnitType
from hvad.admin import TranslatableAdmin, TranslatableModelForm


class AttributeAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(AttributeAdminForm, self).__init__(*args, **kwargs)
        self.fields['unit_type'].queryset = UnitType.objects.language('en').all()
        self.fields['unit_type'].label_from_instance = lambda obj: obj.name


class AttributeAdmin(TranslatableAdmin):
    form = AttributeAdminForm

    list_display = ['pk', 'default_name', 'type', 'multiple']




    class Meta:
        model = Attribute

admin.site.register(Attribute, AttributeAdmin)


class AttributeValueAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(AttributeValueAdminForm, self).__init__(*args, **kwargs)
        self.fields['attribute'].queryset = Attribute.objects.language('en').all()
        self.fields['attribute'].label_from_instance = lambda obj: obj.name


class AttributeValueAdmin(TranslatableAdmin):
    form = AttributeValueAdminForm

    list_display = ['pk', 'default_name', 'attribute_name']

    class Meta:
        model = AttributeValue


admin.site.register(AttributeValue, AttributeValueAdmin)


class AttributeClassificationAdmin(admin.ModelAdmin):
    change_list_template = 'smuggler/change_list.html'
    list_display = [field.name for field in AttributeClassification._meta.fields]
    search_fields = ['attribute_name_en', 'attribute_name_ru', 'slug', 'attribute_value_en', 'attribute_value_ru']

    class Meta:
        model = AttributeClassification


admin.site.register(AttributeClassification, AttributeClassificationAdmin)