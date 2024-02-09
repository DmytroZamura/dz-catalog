from __future__ import unicode_literals

from django.db import models

from hvad.models import TranslatableModel, TranslatedFields
from django.db.models.signals import pre_save, post_save
from autoslug import AutoSlugField
from unidecode import unidecode
from hvad.utils import get_translation
from django.contrib.auth.models import User
from catalog.attribute.models import Attribute

from django.db.models.signals import post_delete
from sorl.thumbnail import ImageField
from catalog.getstream.utils import create_notification_by_instance


class Category(TranslatableModel):
    parent = models.ForeignKey('self', related_name='child_set', null=True, blank=True, default=None,
                               on_delete=models.CASCADE, db_index=True)
    default_name = models.CharField(max_length=150, null=False, blank=True)
    slug = AutoSlugField(populate_from=unidecode('default_name'), db_index=True, editable=True)
    external_code = models.CharField(max_length=15, null=True, blank=True)
    position = models.IntegerField(default=0, db_index=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=150, blank=False, db_index=True),
        description=models.TextField(blank=True),
        name_with_parent=models.CharField(max_length=350, blank=True)
    )

    image = ImageField(null=True, blank=True, upload_to='%Y/%m/%d/')
    background_image = ImageField(null=True, blank=True, upload_to='%Y/%m/%d/')
    content_exists = models.BooleanField(default=False, db_index=True)
    posts_exist = models.BooleanField(default=False, db_index=True)
    users_exist = models.BooleanField(default=False, db_index=True)
    companies_exist = models.BooleanField(default=False, db_index=True)
    products_exist = models.BooleanField(default=False, db_index=True)
    communities_exist = models.BooleanField(default=False, db_index=True)
    first_level = models.BooleanField(default=False, db_index=True)
    approved = models.BooleanField(default=False, blank=True, db_index=True)
    child_qty = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, default=None)
    updated = models.BooleanField(default=False)

    def contents_exist(self, content_type):
        if content_type == 'product' and not self.products_exist:
            self.products_exist = True
            self.save()
        if content_type == 'user' and not self.users_exist:
            self.users_exist = True
            self.save()
        if content_type == 'company' and not self.companies_exist:
            self.companies_exist = True
            self.save()
        if content_type == 'post' and not self.posts_exist:
            self.posts_exist = True
            self.save()
        if content_type == 'community' and not self.communities_exist:
            self.communities_exist = True
            self.save()

    def get_parent_name(self):

        name = ''

        if self.parent:
            parent_obj = get_translation(self.parent, self.language_code)

            name = parent_obj.name_with_parent + ' / '

        return name

    def _get_fullname(self):

        obj = get_translation(self, self.language_code)
        return obj.name_with_parent

    full_name = property(_get_fullname)

    def _get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return None

    image_url = property(_get_image_url)

    def _get_background_image_url(self):
        if self.background_image:
            return self.background_image.url
        else:
            return None

    background_image_url = property(_get_background_image_url)

    # def _get_default_name(self):
    #     obj = get_cached_translation(self)
    #     name = obj.name
    #     return name
    #
    # default_name = property(_get_default_name)

    def _get_name_all_languages(self):
        translations = Category.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.name)
        return values

    name_all_languages = property(_get_name_all_languages)

    @property
    def notification_object_serializer_class(self):
        from .serializers import CategorySerializer

        return CategorySerializer

    # def save(self, *args, **kwargs):
    #
    #     self.name_with_parent = self.get_parent_name() + self.name
    #
    #     return super(Category, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.pk


def update_child_qty_on_delete(sender, instance, **kwargs):
    try:
        if instance.parent:

                parent = Category.objects.get(pk=instance.parent.pk)
                qty = Category.objects.filter(parent=parent.pk).count()
                if qty:
                    parent.child_qty = qty
                else:
                    parent.child_qty = 0
                parent.save()
    except Category.DoesNotExist:
        pass


def update_set_child_qty_on_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Category.objects.get(pk=instance.pk)
            if (old_instance.parent != instance.parent and old_instance.parent != None):
                old_parent = Category.objects.get(pk=old_instance.parent.pk)
                qty = Category.objects.filter(parent=old_parent.pk).count()
                if qty:
                    old_parent.child_qty = qty - 1

                else:
                    old_parent.child_qty = 0
                old_parent.save()
        except Category.DoesNotExist:
            pass


def update_fields_on_save(sender, instance, created, **kwargs):
    try:
        if instance.parent:
            parent = Category.objects.get(pk=instance.parent.pk)
            qty = Category.objects.filter(parent=parent.pk).count()
            if qty:
                parent.child_qty = qty
            else:
                parent.child_qty = 0
            parent.save()
    except Category.DoesNotExist:
        pass


pre_save.connect(update_set_child_qty_on_save, sender=Category)
post_save.connect(update_fields_on_save, sender=Category)
post_delete.connect(update_child_qty_on_delete, sender=Category)


class CategoryClassification(models.Model):
    level1_code = models.IntegerField(blank=True, null=True)
    level1_position = models.IntegerField(default=0)
    level1_en_name = models.CharField(max_length=150, blank=False, null=False, db_index=True)
    level1_ru_name = models.CharField(max_length=150, blank=False, null=False)
    level1_uk_name = models.CharField(max_length=150, blank=False, null=False)
    level2_code = models.IntegerField(blank=True, null=True)
    level2_position = models.IntegerField(default=0)
    level2_en_name = models.CharField(max_length=150, blank=False, null=False, db_index=True)
    level2_ru_name = models.CharField(max_length=150, blank=False, null=False)
    level2_uk_name = models.CharField(max_length=150, blank=False, null=False)
    level3_code = models.IntegerField(blank=True, null=True)
    level3_position = models.IntegerField(default=0)
    level3_en_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    level3_ru_name = models.CharField(max_length=150, blank=True, null=True)
    level3_uk_name = models.CharField(max_length=150, blank=True, null=True)
    level4_code = models.IntegerField(blank=True, null=True)
    level4_position = models.IntegerField(default=0)
    level4_en_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    level4_ru_name = models.CharField(max_length=150, blank=True, null=True)
    level4_uk_name = models.CharField(max_length=150, blank=True, null=True)
    level5_code = models.IntegerField(blank=True, null=True)
    level5_position = models.IntegerField(default=0)
    level5_en_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    level5_ru_name = models.CharField(max_length=150, blank=True, null=True)
    level5_uk_name = models.CharField(max_length=150, blank=True, null=True)
    level6_code = models.IntegerField(blank=True, null=True)
    level6_position = models.IntegerField(default=0)
    level6_en_name = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    level6_ru_name = models.CharField(max_length=150, blank=True, null=True)
    level6_uk_name = models.CharField(max_length=150, blank=True, null=True)

    def __unicode__(self):
        return self.id


class SuggestedCategory(models.Model):
    user = models.ForeignKey(User, related_name='suggested_categories',on_delete=models.CASCADE)
    parent = models.ForeignKey(Category, related_name='suggested_child_set', null=True, blank=True, default=None,
                               on_delete=models.CASCADE)
    name = models.CharField(max_length=150, blank=False)
    reviewed = models.BooleanField(default=False)
    category = models.ForeignKey(Category, related_name='suggestions', null=True, blank=True, default=None,
                                 on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    @property
    def notification_object_serializer_class(self):
        from .serializers import SuggestedCategorySerializer

        return SuggestedCategorySerializer

    def __unicode__(self):
        return self.id


def notify_about_suggestion(sender, instance, created, **kwargs):
    if created:
        create_notification_by_instance(instance)


def notify_suggestion_processed(sender, instance, **kwargs):
    if instance.pk and instance.reviewed:
        old_instance = SuggestedCategory.objects.get(pk=instance.pk)
        if not old_instance.reviewed:
            create_notification_by_instance(instance)


pre_save.connect(notify_suggestion_processed, sender=SuggestedCategory)
post_save.connect(notify_about_suggestion, sender=SuggestedCategory)


class CategoryName(models.Model):
    code = models.CharField(max_length=15, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    lang = models.CharField(max_length=2, blank=False, null=False)

    def __unicode__(self):
        return self.id


class CategoryAttribute(models.Model):
    category = models.ForeignKey(Category, related_name='category_attributes', on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE)
    position = models.IntegerField(default=0, db_index=True)
    default_attribute = models.BooleanField(default=False)
    min = models.PositiveIntegerField(null=True, blank=True, default=0)
    max = models.PositiveIntegerField(null=True, blank=True)
    step = models.PositiveIntegerField(null=True, blank=True, default=1)
    create_date = models.DateTimeField(auto_now_add=True)

    def _get_attribute_name(self):
        obj = get_translation(self.attribute, 'en')
        return obj.name

    attribute_name = property(_get_attribute_name)

    def _get_category_name(self):
        obj = get_translation(self.category, 'en')
        return obj.name

    category_name = property(_get_category_name)

    class Meta:
        unique_together = ("category", "attribute")

    def __unicode__(self):
        return self.id
