from django.core.management.base import BaseCommand
from catalog.company.models import CompanyIndustry, IndustryClassification


def set_industry_translation(instance, name_ru, name_uk):
    try:
        industry = CompanyIndustry.objects.language('ru').get(id=instance.id)
    except CompanyIndustry.DoesNotExist:
        industry = instance.translate('ru')
    industry.name = name_ru
    industry.save()

    try:
        industry = CompanyIndustry.objects.language('uk').get(id=instance.id)
    except CompanyIndustry.DoesNotExist:
        industry = instance.translate('uk')
    industry.name = name_uk
    industry.save()


def check_industry(slug, name_en, name_ru, name_uk):
    try:
        industry = CompanyIndustry.objects.language('en').get(slug=slug)

        print(name_en, name_ru)

        industry.name = name_en

        set_industry_translation(industry, name_ru, name_uk)

        industry.save()

    except CompanyIndustry.DoesNotExist:
        print(name_en, name_ru)
        industry = CompanyIndustry.objects.language('en').create(slug=slug,
                                                                 name=name_en
                                                                 )
        industry.save()
        set_industry_translation(industry, name_ru, name_uk)


def update_industry():
    classification_rows = IndustryClassification.objects.all()
    for classification_row in classification_rows:
        check_industry(classification_row.slug, classification_row.name_en,
                       classification_row.name_ru,
                       classification_row.name_uk)


class Command(BaseCommand):

    def handle(self, *args, **options):
        update_industry()
