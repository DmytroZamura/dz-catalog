from django.core.management.base import BaseCommand
from catalog.general.models import Country, City, Region, UnitTypeClassification, UnitType
import unicodedata as ud



latin_letters = {}


def is_latin(uchr):
    try:
        return latin_letters[uchr]
    except KeyError:
        return latin_letters.setdefault(uchr, 'LATIN' in ud.name(uchr))


def only_roman_chars(unistr):
    return all(is_latin(uchr)
               for uchr in unistr
               if uchr.isalpha())  # isalpha suggested by John Machin


def delete_roman_names(names):
    result = []
    for name in names:
        if not only_roman_chars(name):
            result.append(name)
    return result


def get_ru_name(names, default_name):
    ru_name = default_name

    result = []
    for name in names:
        check_uk_lang = name.upper().find('І')
        if check_uk_lang == -1:
            check_uk_lang = name.upper().find('Ї')
        if check_uk_lang == -1:
            check_uk_lang = name.upper().find('Є')
        if check_uk_lang == -1:
            check_uk_lang = name.upper().find('Ґ')
        if check_uk_lang == -1:
            check_uk_lang = name.find('ʼ')
        if check_uk_lang == -1:
            result.append(name)
    if len(result) > 0:
        if len(result[0]) != 0:
            ru_name = result[0]
    return ru_name


def set_translation_by_alt_names(instance, alt_names, default_name):
    names = delete_roman_names(alt_names.split(";"))
    names_len = len(names)

    en_short_name = default_name
    en_name = default_name
    ru_short_name = default_name
    ru_name = default_name
    uk_short_name = default_name
    uk_name = default_name

    if names_len == 1 and len(names[0]) != 0:
        ru_name = get_ru_name(names, default_name)
        ru_short_name = ru_name
        uk_short_name = names[0]
        uk_name = names[0]

    if names_len > 1:
        check_uk_lang = names[0].upper().find('І')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Ї')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Є')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Ґ')
        if check_uk_lang == -1:
            check_uk_lang = names[0].find('ʼ')

        if check_uk_lang != -1:
            uk_name = names[0]
            uk_short_name = names[0]
            ru_name = get_ru_name(names, default_name)
            ru_short_name = ru_name
        else:
            ru_name = get_ru_name(names, default_name)
            ru_short_name = ru_name
            uk_name = names[names_len - 1]
            uk_short_name = [names_len - 1]

    try:
        country = Country.objects.language('en').get(id=instance.id)
    except Country.DoesNotExist:
        country = instance.translate('en')

    country.name = en_name
    country.short_name = en_short_name
    country.save()

    try:
        country = Country.objects.language('ru').get(id=instance.id)
    except Country.DoesNotExist:
        country = instance.translate('ru')
    country.name = ru_name
    country.short_name = ru_short_name
    country.save()

    try:
        country = Country.objects.language('uk').get(id=instance.id)
    except Country.DoesNotExist:
        country = instance.translate('uk')
    country.name = uk_name
    country.short_name = uk_short_name
    country.save()


def set_region_translation_by_alt_names(instance, alt_names, default_name):
    names = delete_roman_names(alt_names.split(";"))
    names_len = len(names)
    en_name = default_name
    ru_name = default_name
    uk_name = default_name

    if names_len == 1 and len(names[0]) != 0:
        ru_name = get_ru_name(names, default_name)
        uk_name = names[0]

    if names_len > 1:
        check_uk_lang = names[0].upper().find('І')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Ї')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Є')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Ґ')
        if check_uk_lang == -1:
            check_uk_lang = names[0].find('ʼ')

        if check_uk_lang != -1:
            uk_name = names[0]
            ru_name = get_ru_name(names, default_name)
        else:
            ru_name = get_ru_name(names, default_name)
            uk_name = names[names_len - 1]

    try:
        region = Region.objects.language('en').get(id=instance.id)
    except Region.DoesNotExist:
        region = instance.translate('en')

    region.name = en_name
    region.save()

    try:
        region = Region.objects.language('ru').get(id=instance.id)
    except Region.DoesNotExist:
        region = instance.translate('ru')
    region.name = ru_name
    region.save()

    try:
        region = Region.objects.language('uk').get(id=instance.id)
    except Region.DoesNotExist:
        region = instance.translate('uk')
    region.name = uk_name
    region.save()


def set_city_translation_by_alt_names(instance, alt_names, default_name):
    names = delete_roman_names(alt_names.split(";"))
    names_len = len(names)
    en_name = default_name
    ru_name = default_name
    uk_name = default_name

    if names_len == 1 and len(names[0]) != 0:
        ru_name = get_ru_name(names, default_name)
        uk_name = names[0]

    if names_len > 1:
        check_uk_lang = names[0].upper().find('І')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Ї')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Є')
        if check_uk_lang == -1:
            check_uk_lang = names[0].upper().find('Ґ')
        if check_uk_lang == -1:
            check_uk_lang = names[0].find('ʼ')

        if check_uk_lang != -1:
            uk_name = names[0]
            ru_name = get_ru_name(names, default_name)
        else:
            ru_name = get_ru_name(names, default_name)
            uk_name = names[names_len - 1]

    try:
        city = City.objects.language('en').get(id=instance.id)
    except City.DoesNotExist:
        city = instance.translate('en')

    city.name = en_name
    city.save()

    try:
        city = City.objects.language('ru').get(id=instance.id)
    except City.DoesNotExist:
        city = instance.translate('ru')
    city.name = ru_name
    city.save()

    try:
        city = City.objects.language('uk').get(id=instance.id)
    except City.DoesNotExist:
        city = instance.translate('uk')
    city.name = uk_name
    city.save()


def init_countires():
    gcountries = GCountry.objects.all()
    for gcountry in gcountries:
        print(gcountry.name)
        try:
            country = Country.objects.language('en').get(code=gcountry.code3)

            country.code2 = gcountry.code2
            country.tld = gcountry.tld
            country.phone = gcountry.phone
            country.default_name = gcountry.name
            country.geoname_id = gcountry.geoname_id
            country.slug = gcountry.slug
            country.save()

            set_translation_by_alt_names(country, gcountry.alternate_names, gcountry.name)




        except Country.DoesNotExist:
            country = Country.objects.language('en').create(code=gcountry.code3, code2=gcountry.code2,
                                                            tld=gcountry.tld, phone=gcountry.phone,
                                                            default_name=gcountry.name, name=gcountry.name,
                                                            short_name=gcountry.name,
                                                            geoname_id=gcountry.geoname_id, slug=gcountry.slug)

            set_translation_by_alt_names(country, gcountry.alternate_names, gcountry.name)


def init_cities():
    gcities = GCity.objects.all()
    for gcity in gcities:
        print(gcity.name)
        country = Country.objects.language('en').get(geoname_id=gcity.country.geoname_id)
        if gcity.region:
            region = Region.objects.language('en').get(geoname_id=gcity.region.geoname_id)
        else:
            region = None
        try:
            city = City.objects.language('en').get(geoname_id=gcity.geoname_id)
            city.country = country
            city.region = region
            city.default_name = gcity.name
            city.geoname_id = gcity.geoname_id
            city.slug = gcity.slug
            city.latitude = gcity.latitude
            city.longitude = gcity.longitude
            city.population = gcity.population
            city.timezone = gcity.timezone
            city.save()

            set_city_translation_by_alt_names(city, gcity.alternate_names, gcity.name)


        except City.DoesNotExist:
            city = City.objects.language('en').create(country=country, region=region,
                                                      default_name=gcity.name, name=gcity.name,
                                                      geoname_id=gcity.geoname_id, slug=gcity.slug,
                                                      latitude=gcity.latitude,
                                                      longitude=gcity.longitude,
                                                      population=gcity.population,
                                                      timezone=gcity.timezone
                                                      )

            set_city_translation_by_alt_names(city, gcity.alternate_names, gcity.name)


def init_regions():
    gregions = GRegion.objects.all()
    for gregion in gregions:
        print(gregion.name)
        country = Country.objects.language('en').get(geoname_id=gregion.country.geoname_id)
        try:
            region = Region.objects.language('en').get(geoname_id=gregion.geoname_id)
            region.country = country
            region.default_name = gregion.name
            region.geoname_id = gregion.geoname_id
            region.slug = gregion.slug
            region.save()

            set_region_translation_by_alt_names(region, gregion.alternate_names, gregion.name)


        except Region.DoesNotExist:
            region = Region.objects.language('en').create(country=country,
                                                          default_name=gregion.name, name=gregion.name,
                                                          geoname_id=gregion.geoname_id, slug=gregion.slug
                                                          )

            set_region_translation_by_alt_names(region, gregion.alternate_names, gregion.name)


def check_regions_duplicates():
    regions = Region.objects.language('en').all()
    for region in regions:
        count = Region.objects.language('en').filter(slug=region.slug).count()
        if count > 1:
            dub_regions = Region.objects.language('en').filter(slug=region.slug)

            for dublicate in dub_regions:
                new_slug = dublicate.country.slug + '-' + dublicate.slug
                print(new_slug)
                dublicate.slug = new_slug
                dublicate.save()

def check_null_slug():
    null_objs = JobType.objects.filter(slug__isnull=True)

    for null_obj in null_objs:
        print(null_obj.default_name)


def check_cities_duplicates():
    cities = City.objects.language('en').all()
    for city in cities:
        count = City.objects.language('en').filter(slug=city.slug).count()
        if count > 1:
            dub_cities = City.objects.language('en').filter(slug=city.slug)

            for dublicate in dub_cities:
                new_slug = dublicate.slug + '-' + dublicate.region.slug
                print(new_slug)
                dublicate.slug = new_slug
                dublicate.save()


def set_uom_translation(instance, name_ru, name_ru_pl, code_ru, name_uk, name_uk_pl, code_uk):
    try:
        uom = UnitType.objects.language('ru').get(id=instance.id)
    except UnitType.DoesNotExist:
        uom = instance.translate('ru')
    uom.name = name_ru
    uom.name_plural = name_ru_pl
    uom.code = code_ru
    uom.save()

    try:
        uom = UnitType.objects.language('uk').get(id=instance.id)
    except UnitType.DoesNotExist:
        uom = instance.translate('uk')
    uom.name = name_uk
    uom.name_plural = name_uk_pl
    uom.code = code_uk
    uom.save()


def check_uom(name_en, name_en_pl, code_en, name_ru, name_ru_pl, code_ru, name_uk, name_uk_pl, code_uk):
    try:
        uom = UnitType.objects.language('en').get(code=code_en)

        print(name_en, name_ru)

        uom.name = name_en

        uom.name_plural = name_en_pl
        uom.code = code_en
        set_uom_translation(uom, name_ru, name_ru_pl, code_ru, name_uk, name_uk_pl, code_uk)

        uom.save()

    except UnitType.DoesNotExist:
        print(name_en, name_ru)
        uom = UnitType.objects.language('en').create(code=code_en,
                                                     name=name_en,
                                                     name_plural=name_en_pl
                                                     )
        uom.save()
        set_uom_translation(uom, name_ru, name_ru_pl, code_ru, name_uk, name_uk_pl, code_uk)


def update_uom():
    classification_rows = UnitTypeClassification.objects.all()
    for classification_row in classification_rows:
        check_uom(classification_row.name_en, classification_row.name_en_pl, classification_row.code_en,
                  classification_row.name_ru, classification_row.name_ru_pl, classification_row.code_ru,
                  classification_row.name_uk, classification_row.name_uk_pl, classification_row.code_uk)


class Command(BaseCommand):

    def handle(self, *args, **options):
        check_null_slug()
        # check_regions_duplicates()
        # check_cities_duplicates()
        # update_uom()

        # init_countires()
        # print(len(''.split(";")))
        # print(only_roman_chars(u"russian: "))
        # names = 'Автономна Республіка Крим;Автономная Республика Крым;Республика Крым;Республіка Крим'.split(";")
        # print(delete_roman_names(names))
        # print(get_ru_name(['Кіфісія'],'Kifisiá'))
