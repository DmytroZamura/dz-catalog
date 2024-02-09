from __future__ import unicode_literals

from catalog.company.models import Company
from catalog.user_profile.models import UserProfile
from catalog.general.models import Country, City

from django.db import models

from hvad.models import TranslatableModel, TranslatedFields
from django.db.models import Max
from django.db.models.signals import post_delete, pre_save, post_save
from hvad.utils import get_translation


class UserProfileEmployment(TranslatableModel):
    id = models.BigAutoField(primary_key=True)
    profile = models.ForeignKey(UserProfile, related_name='employment')
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL, related_name='employees')
    company_name = models.CharField(max_length=100, null=True, blank=True)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    present_time = models.BooleanField(default=True)
    education = models.BooleanField(default=False)
    translations = TranslatedFields(
        title=models.CharField(max_length=100, null=True, blank=True),
        description=models.TextField(null=True, blank=True)
    )
    position = models.PositiveIntegerField(null=True, blank=True)

    def _get_name_all_languages(self):
        translations = UserProfileEmployment.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:

            values.append(translation.title)
            if translation.company:
                values.extend(translation.company.name_all_languages)
        return values

    def _get_description_all_languages(self):
        translations = UserProfileEmployment.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.description)
        return values

    name_all_languages = property(_get_name_all_languages)
    description_all_languages = property(_get_description_all_languages)

    def update_company_qty(self, qty):
        if self.company:
            if self.education:
                self.company.eventsqty.update_events_qty('students', qty)
            else:
                self.company.eventsqty.update_events_qty('employees', qty)

    def save(self, *args, **kwargs):
        if self.position is None:
            try:

                max_position = UserProfileEmployment.objects.filter(profile=self.profile).aggregate(Max('position'))

                self.position = (max_position.get("position__max") or 0) + 1
            except:
                self.position = 1
        return super(UserProfileEmployment, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id


def update_related_objects_on_delete(sender, instance, **kwargs):
    instance.update_company_qty(-1)


def update_related_objects_on_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_object = UserProfileEmployment.objects.get(pk=instance.pk)

        except:
            old_object = None

        if old_object is not None:
            if old_object.company != instance.company:
                old_object.update_company_qty(-1)
                if instance.company:
                    instance.update_company_qty(1)
                else:
                    if not instance.company_name:
                        translation = get_translation(old_object.company, 'en')
                        instance.company_name = translation.name


def update_related_objects_on_create(sender, instance, created, **kwargs):
    if created:
        instance.update_company_qty(1)


post_save.connect(update_related_objects_on_create, sender=UserProfileEmployment)

pre_save.connect(update_related_objects_on_save, sender=UserProfileEmployment)

post_delete.connect(update_related_objects_on_delete, sender=UserProfileEmployment)
