from __future__ import unicode_literals

from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from catalog.utils.utils import get_default_name
from django.core.exceptions import ObjectDoesNotExist


class Currency(TranslatableModel):
    code = models.CharField(max_length=9, unique=True, db_index=True)
    number = models.CharField(max_length=3, null=True, unique=True)
    default_name = models.CharField(max_length=60, null=True, blank=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=40, db_index=True)
    )

    def __unicode__(self):
        return self.code


class Country(TranslatableModel):
    currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.CASCADE)
    geoname_id = models.PositiveIntegerField(null=True, blank=True)
    slug = models.CharField(max_length=60, null=True, blank=True, unique=True, db_index=True)
    code = models.CharField(max_length=3, null=True, unique=True)
    code2 = models.CharField(max_length=3, null=True, blank=True)
    tld = models.CharField(max_length=3, null=True, blank=True)
    phone = models.CharField(max_length=25, null=True, blank=True)
    default_name = models.CharField(max_length=60, null=True, blank=True)
    flag = models.FileField(null=True, blank=True, upload_to='%Y/%m/%d/')
    posts_exist = models.BooleanField(default=False)
    users_exist = models.BooleanField(default=False)
    companies_exist = models.BooleanField(default=False)
    products_exist = models.BooleanField(default=False)
    communities_exist = models.BooleanField(default=False)
    translations = TranslatedFields(
        name=models.CharField(max_length=100, db_index=True),
        short_name=models.CharField(max_length=100, db_index=True)
    )

    def _get_flag_url(self):
        if self.flag:
            return self.flag.url
        else:
            return None

    flag_url = property(_get_flag_url)

    def _get_name_all_languages(self):
        translations = Country.objects.language('all').filter(pk=self.pk)
        names = []
        for translation in translations:
            names.append(translation.name)
        return names

    name_all_languages = property(_get_name_all_languages)

    def __unicode__(self):
        return self.code


class Region(TranslatableModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    default_name = models.CharField(max_length=60, null=True, blank=True)
    geoname_id = models.PositiveIntegerField(null=True, blank=True)
    slug = models.CharField(max_length=60, unique=True, db_index=True, null=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=60, db_index=True)
    )

    def __unicode__(self):
        return self.default_name


class City(TranslatableModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_index=True)
    region = models.ForeignKey(Region, null=True, blank=True, related_name='region_cities', on_delete=models.CASCADE,
                               db_index=True)
    default_name = models.CharField(max_length=60, null=True, blank=True)
    geoname_id = models.PositiveIntegerField(null=True, blank=True)
    slug = models.CharField(max_length=60, db_index=True, blank=True, null=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=60, db_index=True)
    )
    latitude = models.DecimalField(null=True,
                                   blank=True,
                                   decimal_places=15,
                                   max_digits=19,
                                   default=0)
    longitude = models.DecimalField(null=True,
                                    blank=True,
                                    decimal_places=15,
                                    max_digits=19,
                                    default=0)
    population = models.PositiveIntegerField(null=True, blank=True)
    timezone = models.CharField(max_length=35, null=True, blank=True)
    posts_exist = models.BooleanField(default=False, db_index=True)
    users_exist = models.BooleanField(default=False, db_index=True)
    companies_exist = models.BooleanField(default=False, db_index=True)
    products_exist = models.BooleanField(default=False, db_index=True)
    communities_exist = models.BooleanField(default=False, db_index=True)

    emblem = models.FileField(null=True, blank=True, upload_to='%Y/%m/%d/')
    head_photo = models.FileField(null=True, blank=True, upload_to='%Y/%m/%d/')

    def _get_emblem_url(self):
        if self.emblem:
            return self.emblem.url
        else:
            return None

    emblem_url = property(_get_emblem_url)

    def _get_head_photo_url(self):
        if self.head_photo:
            return self.head_photo.url
        else:
            return None

    head_photo_url = property(_get_head_photo_url)

    @property
    def location_field_indexing(self):
        """Location for indexing.
        """
        return {
            'lat': self.latitude,
            'lon': self.longitude,
        }

    def __unicode__(self):
        return self.default_name


class Language(TranslatableModel):
    code = models.CharField(max_length=3, unique=True)
    locale_lang = models.BooleanField(default=False)
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )

    def __unicode__(self):
        return self.code


class UnitType(TranslatableModel):
    default_name = property(get_default_name)
    translations = TranslatedFields(
        code=models.CharField(max_length=10, unique=False),
        name=models.CharField(max_length=40),
        name_plural=models.CharField(max_length=40, null=True, blank=True)
    )

    def __unicode__(self):
        return self.id


class UnitTypeClassification(models.Model):
    name_en = models.CharField(max_length=40)
    name_en_pl = models.CharField(max_length=40)
    name_ru = models.CharField(max_length=40)
    name_ru_pl = models.CharField(max_length=40)
    name_uk = models.CharField(max_length=40)
    name_uk_pl = models.CharField(max_length=40)
    code_en = models.CharField(max_length=10, unique=True)
    code_ru = models.CharField(max_length=10, unique=True)
    code_uk = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return self.id


class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, related_name='rates', on_delete=models.CASCADE)
    currency_to = models.ForeignKey(Currency, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=24, decimal_places=12, blank=False, null=False)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("currency", "currency_to")

    def _get_currency_code(self):
        obj = self.currency.code
        return obj

    def _get_currency_to_code(self):
        obj = self.currency_to.code
        return obj

    currency_code = property(_get_currency_code)
    currency_to_code = property(_get_currency_to_code)

    def __unicode__(self):
        return "%s  %s  %s" % (self.currency.code, self.currency_to_code, self.update_date)


def convert_price(price, currency_from, currency_to, rate_usd=None):
    if currency_from == currency_to:
        new_price = price

    else:
        try:
            rate_usd_obj = CurrencyRate.objects.get(currency=currency_from, currency_to=1)
            rate_cur_from_to_usd = rate_usd_obj.rate
            new_price_usd = price / rate_cur_from_to_usd
            if currency_to == 1:
                new_price = round(new_price_usd, 2)
            else:
                try:
                    if not rate_usd:
                        rate_to_usd = CurrencyRate.objects.get(currency=currency_to, currency_to=1)
                        rate_usd = rate_to_usd.rate
                    new_price = round(new_price_usd * rate_usd, 2)

                except CurrencyRate.DoesNotExist:
                    new_price = None
        except CurrencyRate.DoesNotExist:
            new_price = None
    return new_price


class JobType(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )

    position = models.IntegerField(default=0)
    slug = models.CharField(max_length=60, null=True, blank=True, db_index=True)
    default_name = property(get_default_name)

    def _get_name_all_languages(self):
        translations = JobType.objects.language('all').filter(pk=self.pk)
        names = []
        for translation in translations:
            names.append(translation.name)
        return names

    name_all_languages = property(_get_name_all_languages)

    class Meta:
        ordering = ["position"]

    def __unicode__(self):
        return self.id


class JobFunction(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=80)
    )
    position = models.IntegerField(default=0)
    slug = models.CharField(max_length=60, null=True, blank=True, db_index=True)
    default_name = property(get_default_name)

    def _get_name_all_languages(self):
        translations = JobFunction.objects.language('all').filter(pk=self.pk)
        names = []
        for translation in translations:
            names.append(translation.name)
        return names

    name_all_languages = property(_get_name_all_languages)

    def __unicode__(self):
        return self.id


class SeniorityLabel(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=80)
    )
    position = models.IntegerField(default=0)
    slug = models.CharField(max_length=60, null=True, blank=True, db_index=True)
    default_name = property(get_default_name)

    def _get_name_all_languages(self):
        translations = SeniorityLabel.objects.language('all').filter(pk=self.pk)
        names = []
        for translation in translations:
            names.append(translation.name)
        return names

    name_all_languages = property(_get_name_all_languages)

    class Meta:
        ordering = ["position"]

    def __unicode__(self):
        return self.id


def get_translation_by_code(code, lang):
    try:
        translation = Translation.objects.language(lang).fallbacks('en').get(code=code)
        text = translation.text
    except ObjectDoesNotExist:
        text = ''
    return text


class Translation(TranslatableModel):
    code = models.CharField(max_length=30, unique=True)
    translations = TranslatedFields(
        text=models.TextField(null=True, blank=True),
    )

    class Meta:
        indexes = [
            models.Index(fields=['code', ]),
        ]

    def __unicode__(self):
        return self.code
