from __future__ import unicode_literals

from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from hvad.utils import get_translation

from catalog.general.models import UnitType


def _get_default_name(self):
    obj = get_translation(self, self.language_code)
    return obj.name

ATTRIBUTE_TYPES = [
        (1, "1. list"),
        (2, "2. number"),
        (3, "3. string"),
        (4, "4. boolean"),
        (5, "5. integer"),
    ]

class Attribute(TranslatableModel):


    type = models.IntegerField(choices=ATTRIBUTE_TYPES, default=1)
    multiple = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, blank=True, null=True, on_delete=models.SET_NULL)
    slug = models.CharField(max_length=60, null=True, blank=True)
    updated = models.BooleanField(default=False)

    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )



    default_name = property(_get_default_name)

    def __unicode__(self):
        return self.id


class AttributeValue(TranslatableModel):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )

    default_name = property(_get_default_name)

    def _get_attribute_name(self):
        obj = get_translation(self.attribute, self.language_code)
        return obj.name

    attribute_name = property(_get_attribute_name)

    def __unicode__(self):
        return self.id



class AttributeClassification(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=True, blank=True)
    slug = models.CharField(max_length=60, null=True, blank=True)
    type = models.IntegerField(choices=ATTRIBUTE_TYPES, default=1)
    multiple = models.BooleanField(default=False)
    unit_type = models.ForeignKey(UnitType, blank=True, null=True, on_delete=models.SET_NULL)
    attribute_name_en=models.CharField(max_length=40)
    attribute_name_ru = models.CharField(max_length=40)
    attribute_name_uk = models.CharField(max_length=40)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, null=True, blank=True)
    attribute_value_en = models.CharField(max_length=40, null=True, blank=True)
    attribute_value_ru = models.CharField(max_length=40, null=True, blank=True)
    attribute_value_uk = models.CharField(max_length=40, null=True, blank=True)

    def __unicode__(self):
        return self.id


