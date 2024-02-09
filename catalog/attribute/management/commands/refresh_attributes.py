from django.core.management.base import BaseCommand

from catalog.attribute.models import Attribute, AttributeValue, AttributeClassification


def set_attribute_value__translation(instance: AttributeValue, name, lang_code):
    try:
        value = AttributeValue.objects.language(lang_code).get(id=instance.id)
    except:
        value = instance.translate(lang_code)
    value.name = name

    try:
        value.save()
    except:
        print('Ошибка - ' + name)


def set_attribute_translation(instance: Attribute, name, lang_code):
    try:
        attribute = Attribute.objects.language(lang_code).get(id=instance.id)
    except:
        attribute = instance.translate(lang_code)
    attribute.name = name

    try:
        attribute.save()
    except:
        print('Ошибка - ' + name)


def check_attribute(classification: AttributeClassification):
    if classification.attribute:
        attribute = Attribute.objects.language('en').get(pk=classification.attribute.pk)
    else:
        try:
            attribute = Attribute.objects.language('en').get(slug=classification.slug)
        except Attribute.DoesNotExist:
            attribute = Attribute.objects.language('en').create(
            )

    if not attribute.updated:
        print(classification.attribute_name_ru)
        attribute.slug = classification.slug
        attribute.unit_type = classification.unit_type
        attribute.multiple = classification.multiple
        attribute.type = classification.type
        attribute.name = classification.attribute_name_en
        attribute.updated = True
        attribute.save()
        set_attribute_translation(attribute, classification.attribute_name_ru, 'ru')
        set_attribute_translation(attribute, classification.attribute_name_uk, 'uk')
        AttributeClassification.objects.filter(slug=classification.slug).update(attribute=attribute)

    if classification.attribute_value_en:
        if classification.attribute_value:
            value = AttributeValue.objects.language('en').get(pk=classification.attribute_value.pk)
        else:
            value = AttributeValue.objects.language('en').create(attribute=attribute,
                                                                 name=classification.attribute_value_en
                                                                 )
        value.save()

        set_attribute_value__translation(value, classification.attribute_value_ru, 'ru')
        set_attribute_value__translation(value, classification.attribute_value_uk, 'uk')
        AttributeClassification.objects.filter(slug=classification.slug,
                                               attribute_value_en=classification.attribute_value_en).update(
            attribute_value=value)

        print('Value: ' + classification.attribute_value_ru)

    return attribute


def refresh_attributes():
    Attribute.objects.language('en').all().update(updated=False)
    classification_rows = AttributeClassification.objects.all()
    for classification_row in classification_rows.all():
        attribute = check_attribute(classification_row)
        if classification_row.attribute != attribute:
            classification_row.attribute = attribute
            classification_row.save()

def create_attributes():

    classification_rows = AttributeClassification.objects.filter(attribute__isnull=True)
    for classification_row in classification_rows.all():
        attribute = check_attribute(classification_row)
        if classification_row.attribute != attribute:
            classification_row.attribute = attribute
            classification_row.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        # create_attributes()
        refresh_attributes()
