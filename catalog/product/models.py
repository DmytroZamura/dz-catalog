from __future__ import unicode_literals

from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from django.db.models import Max
from django.contrib.auth.models import User
from catalog.general.models import Country, City, UnitType, Currency, convert_price
from catalog.file.models import UserImage
from catalog.category.models import Category, SuggestedCategory
from catalog.attribute.models import Attribute, AttributeValue
from catalog.company.models import Company, CompanyCategory
from catalog.user_profile.models import UserProfileCategory
from django.db.models.signals import post_save, post_delete, pre_save
from taggit.managers import TaggableManager
from django.core.exceptions import ObjectDoesNotExist
from hvad.utils import get_translation
from django.conf import settings
from django.db.models import Q
from django.utils import translation
from catalog.utils.utils import unique_slugify
from catalog.utils.model_mixins import UpdateQtyMixin


class ProductGroup(TranslatableModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='child_set', null=True, blank=True, default=None,
                               on_delete=models.CASCADE)
    translations = TranslatedFields(
        name=models.CharField(max_length=150)
    )
    child_qty = models.IntegerField(default=0)

    def _get_name_all_languages(self):
        translations = ProductGroup.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.name)
        return values

    name_all_languages = property(_get_name_all_languages)

    def __unicode__(self):
        return self.id


def update_product_group_child_qty_on_delete(sender, instance, **kwargs):
    if (instance.parent_id):
        try:
            parent = ProductGroup.objects.get(pk=instance.parent.pk)
            qty = ProductGroup.objects.filter(parent=parent.pk).count()
            if qty:
                parent.child_qty = qty
            else:
                parent.child_qty = 0
            parent.save()
        except:
            return None


def update_product_group_fields_on_save(sender, instance, created, **kwargs):
    if instance.parent:
        parent = ProductGroup.objects.get(pk=instance.parent.pk)
        qty = ProductGroup.objects.filter(parent=parent.pk).count()
        if qty:
            parent.child_qty = qty
        else:
            parent.child_qty = 0
        parent.save()


post_save.connect(update_product_group_fields_on_save, sender=ProductGroup)
post_delete.connect(update_product_group_child_qty_on_delete, sender=ProductGroup)


class Product(TranslatableModel):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='user_products')
    company = models.ForeignKey(Company, blank=True, null=True, related_name='company_products',
                                on_delete=models.SET_NULL)
    slug = models.CharField(max_length=500, blank=True, null=True, db_index=True)
    product_group = models.ForeignKey(ProductGroup, blank=True, null=True, on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    suggested_category = models.ForeignKey(SuggestedCategory, blank=True, null=True, on_delete=models.SET_NULL)
    model_number = models.CharField(max_length=40, null=True, blank=True)
    brand_name = models.CharField(max_length=60, null=True, blank=True)
    origin = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    product_or_service = models.BooleanField(default=True)
    unit_type = models.ForeignKey(UnitType, null=True, blank=True, on_delete=models.SET_NULL)
    published = models.BooleanField(default=False, db_index=True)
    deleted = models.BooleanField(default=False, db_index=True)
    price_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price_to = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price_usd_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price_usd_to = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2, db_index=True)
    discount = models.IntegerField(null=True, blank=True, db_index=True)
    discount_price_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount_price_to = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount_price_usd_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount_price_usd_to = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    deadline = models.DateField(null=True, blank=True)
    weight_kg = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)

    one_price = models.BooleanField(default=True)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    link_to_buy = models.URLField(blank=True, null=True)
    tags = TaggableManager(blank=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=150),
        short_description=models.TextField(null=True, blank=True),
        packaging_and_delivery=models.TextField(null=True, blank=True),
        price_conditions=models.TextField(null=True, blank=True),
        seo_title = models.CharField(max_length=150, null=True, blank=True),
        seo_description=models.CharField(max_length=400, null=True, blank=True),
    )
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, db_index=True)

    def get_absolute_url(self):

        if self.slug:
            subject = 'u'
            sslug = self.user.user_profile.slug

            if self.company:
                subject = 'c'
                sslug = self.company.slug

            url = '/product/' + subject + '/' + sslug + '/' + self.slug
        else:

            url = '/product/' + str(self.id)

        url = url + '/' + self.language_code

        return url

    def get_email_dict(self, lang):
        try:
            trans = get_translation(self, lang)
        except ObjectDoesNotExist:
            trans = get_translation(self, 'en')
        name = trans.name
        url = settings.FRONTEND_URL + 'product/' + self.id
        if self.images.exists():
            img_obj = self.images.first()
            image = img_obj.image.file.url
        else:
            image = settings.FRONTEND_URL + 'static/assets/img/default_product.png'
        res = dict()
        res['name'] = name
        res['url'] = url
        res['image'] = image

    def smart_delete(self):
        product = self
        product.deleted = True
        product.published = False
        product.save()

        images = product.images
        images.all().delete()

        product_categories = product.product_categories
        product_categories.all().delete()

        attributes = product.attributes
        attributes.all().delete()

        favorites = product.favorites
        favorites.all().delete()

        try:
            posts = product.product_posts
            for post in posts.all():
                post.smart_delete()

        except ObjectDoesNotExist:
            pass

        try:
            posts = product.product_reviews
            for post in posts.all():
                post.smart_delete()
        except ObjectDoesNotExist:
            pass

    def save(self, *args, **kwargs):
        if self.price_from and self.currency:
            self.price_usd_from = convert_price(self.price_from, self.currency.id, 1)
        if self.price_to and self.currency:
            self.price_usd_to = convert_price(self.price_to, self.currency.id, 1)
        if self.discount_price_to and self.currency:
            self.discount_price_usd_to = convert_price(self.discount_price_to, self.currency.id, 1)
        if self.discount_price_from and self.currency:
            self.discount_price_usd_from = convert_price(self.discount_price_from, self.currency.id, 1)

        return super(Product, self).save(*args, **kwargs)

    def _get_name_all_languages(self):
        translations = Product.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.name)
        return values

    def _get_description_all_languages(self):
        translations = Product.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.short_description)
        return values

    def _get_packaging_and_delivery_all_languages(self):
        translations = Product.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.packaging_and_delivery)
        return values

    def _get_price_conditions_all_languages(self):
        translations = Product.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.price_conditions)
        return values

    def update_foreign_instances_qty(self, qty):
        if self.company:
            self.company.eventsqty.update_events_qty('products', qty)

        if self.company is None:
            self.user.user_profile.eventsqty.update_events_qty('products', qty)

    def update_rating(self, reviews, rating):
        try:
            if self.eventsqty is not None:
                if self.eventsqty.related_reviews + reviews > 0:
                    new_rating = ((self.eventsqty.related_reviews * self.eventsqty.rating) + reviews * rating) / (
                            self.eventsqty.related_reviews + reviews)
                else:
                    new_rating = 0
                self.eventsqty.related_reviews = self.eventsqty.related_reviews + reviews
                self.eventsqty.rating = new_rating
                if self.eventsqty.related_reviews >= 0:
                    self.eventsqty.save()
        except ProductEventsQty.DoesNotExist:
            pass

    def check_seo_data(self):

        if self.company:
            country = self.company.country
            city = self.company.city
        else:
            country = self.user.user_profile.country
            city = self.user.user_profile.city
        if country:
            check_seo_data_exists(None, country, None)
        if city:
            check_seo_data_exists(None, country, city)

    name_all_languages = property(_get_name_all_languages)
    description_all_languages = property(_get_description_all_languages)
    price_conditions_all_languages = property(_get_price_conditions_all_languages)
    packaging_and_delivery_all_languages = property(_get_packaging_and_delivery_all_languages)

    @property
    def notification_object_serializer_class(self):
        from .serializers import ProductShortSerializer

        return ProductShortSerializer

    @property
    def activity_object_serializer_class(self):
        from .serializers import ProductShortSerializer

        return ProductShortSerializer

    @property
    def country_indexing(self):
        """Tags for indexing.

                Used in Elasticsearch indexing.
                """

        country = None
        if self.company:
            if self.company.country:
                country = self.company.country.id
        else:
            if self.user:
                if self.user.user_profile:
                    if self.user.user_profile.country:
                        country = self.user.user_profile.country.id

        return country

    @property
    def region_indexing(self):
        """Tags for indexing.

                Used in Elasticsearch indexing.
                """
        region = None
        if self.company:
            if self.company.city:
                region = self.company.city.region.id
        else:
            if self.user:
                if self.user.user_profile:
                    if self.user.user_profile.city:
                        region = self.user.user_profile.city.region.id

        return region

    @property
    def city_indexing(self):
        """Tags for indexing.

                Used in Elasticsearch indexing.
                """
        city = None
        if self.company:
            if self.company.city:
                city = self.company.city.id
        else:
            if self.user:
                if self.user.user_profile:
                    if self.user.user_profile.city:
                        city = self.user.user_profile.city.id

        return city

    @property
    def city_name_indexing(self):
        """Tags for indexing.

                Used in Elasticsearch indexing.
                """
        city_name = None
        if self.company:
            city_name = self.company.city_name
        else:
            if self.user:
                if self.user.user_profile:
                    city_name = self.user.user_profile.city_name

        return city_name

    @property
    def tags_indexing(self):

        """Tags for indexing.

              Used in Elasticsearch indexing.

                  """
        product = Product.objects.language('en').get(pk=self.id)
        values = []
        if product.tags:
            for tag in product.tags.all():
                values.append(tag.name)
        return values

    @property
    def categories_indexing(self):
        """Tags for indexing.

        Used in Elasticsearch indexing.
        """

        values = []
        for category in self.product_categories.all():
            values.append(category.category_id)
        return values

    @property
    def location_field_indexing(self):
        latitude = 0
        longitude = 0

        if self.company:
            if self.company.city:
                latitude = self.company.city.latitude
                longitude = self.company.city.longitude
        else:
            if self.user:
                if self.user.user_profile:
                    if self.user.user_profile.city:
                        latitude = self.user.user_profile.city.latitude
                        longitude = self.user.user_profile.city.longitude

        return {
            'lat': latitude,
            'lon': longitude,
        }

    unique_together = ("user", "company", "slug")

    def __unicode__(self):
        return self.id


class ProductEventsQty(UpdateQtyMixin, models.Model):
    product = models.OneToOneField(Product, related_name='eventsqty', primary_key=True)
    publications = models.PositiveIntegerField(default=0)

    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1, db_index=True)
    videos = models.PositiveIntegerField(default=0)
    questions = models.PositiveIntegerField(default=0)
    reviews = models.PositiveIntegerField(default=0)
    related_questions = models.PositiveIntegerField(default=0, db_index=True)
    related_reviews = models.PositiveIntegerField(default=0, db_index=True)

    def __unicode__(self):
        return self.id


def create_related_objects_categories(instance):
    if instance.category != None:
        if instance.company:
            exist = CompanyCategory.objects.filter(company=instance.company, category=instance.category,
                                                   interest=False).exists()
            if not exist:
                object = CompanyCategory(company=instance.company, category=instance.category, interest=False,
                                         products_qty=1)
                object.save()
            else:
                object = CompanyCategory.objects.get(company=instance.company, category=instance.category,
                                                     interest=False)
                object.products_qty = object.products_qty + 1
                object.save()

        if not instance.company:
            exist = UserProfileCategory.objects.filter(profile__user=instance.user, category=instance.category,
                                                       interest=False).exists()
            if not exist:
                object = UserProfileCategory(profile_id=instance.user.user_profile.pk, category=instance.category,
                                             interest=False, products_qty=1)
                object.save()
            else:
                object = UserProfileCategory.objects.get(profile_id=instance.user.user_profile.pk,
                                                         category=instance.category,
                                                         interest=False)
                object.products_qty = object.products_qty + 1
                object.save()


def create_product_objects_after_product_save(sender, instance, created, **kwargs):
    if created:

        object = ProductEventsQty(product=instance)
        object.save()

        if instance.product_group:
            object = ProductGroupItem(product_id=instance.pk, group=instance.product_group)
            object.save()
        if instance.category:
            object = ProductCategory(product_id=instance.pk, category=instance.category)
            object.save()

        create_related_objects_categories(instance)

        if instance.published:
            instance.update_foreign_instances_qty(1)


def check_product_objects_on_product_save(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_product = Product.objects.language().fallbacks('en').get(pk=instance.pk)
            old_group = old_product.product_group
            old_category = old_product.category
            old_published = old_product.published
        except:
            old_group = None
            old_category = None
            old_published = None

        if old_group != instance.product_group:
            if old_group != None:
                ProductGroupItem.objects.filter(product=instance.pk).delete()
            object = ProductGroupItem(product_id=instance.pk, group=instance.product_group)
            object.save()

        if old_category != instance.category:
            if old_category:
                ProductCategory.objects.filter(product=instance.pk).delete()
                if instance.company:
                    object = CompanyCategory.objects.get(company=instance.company, category=old_category,
                                                         interest=False)
                    update_related_category_objects(object)

                if not instance.company:
                    try:
                        object = UserProfileCategory.objects.get(profile__user=instance.user, category=old_category,
                                                                 interest=False)
                        update_related_category_objects(object)
                    except models.ObjectDoesNotExist:
                        pass

            if instance.category:
                object = ProductCategory(product_id=instance.pk, category=instance.category)
                object.save()
                create_related_objects_categories(instance)

        if old_published is not None:
            if old_published != instance.published:
                if instance.published:

                    qty = 1
                    if not instance.slug:
                        if instance.company:
                            queryset = Product.objects.untranslated().filter(company=instance.company)
                        else:
                            queryset = Product.objects.untranslated().filter(user=instance.user)

                        en_object = Product.objects.language('en').get(id=instance.id)
                        if en_object.name:
                            unique_slugify(instance, en_object.name, queryset=queryset)

                else:
                    qty = -1
                instance.update_foreign_instances_qty(qty)


def update_objects_on_product_delete(sender, instance, **kwargs):
    if instance.category != None:
        if instance.company:
            object = CompanyCategory.objects.get(company=instance.company, category=instance.category,
                                                 interest=False)
            update_related_category_objects(object)

        if not instance.company:
            object = UserProfileCategory.objects.get(profile__user=instance.user, category=instance.category,
                                                     interest=False)
            update_related_category_objects(object)

        if instance.published:
            instance.update_foreign_instances_qty(-1)


def update_related_category_objects(object):
    if object.products_qty <= 1:
        if object.child_qty == 0:
            object.delete()
        else:
            object.products_qty = 0
            object.save()
    else:
        object.products_qty = object.products_qty - 1
        object.save()


def update_general_info_on_product_save(sender, instance, created, **kwargs):
    if created:
        instance.check_seo_data()

        if instance.company:
            if instance.company.country:
                if not instance.company.country.products_exist:
                    instance.company.country.products_exist = True
                    instance.company.country.save()
            if instance.company.city:
                if not instance.company.city.products_exist:
                    instance.company.city.products_exist = True
                    instance.company.city.save()
        if instance.user:
            if instance.user.user_profile.country:
                if not instance.user.user_profile.country.products_exist:
                    instance.user.user_profile.country.products_exist = True
                    instance.user.user_profile.country.save()
            if instance.user.user_profile.city:
                if not instance.user.user_profile.city.products_exist:
                    instance.user.user_profile.city.products_exist = True
                    instance.user.user_profile.city.save()


post_save.connect(update_general_info_on_product_save, sender=Product)
post_save.connect(create_product_objects_after_product_save, sender=Product)

pre_save.connect(check_product_objects_on_product_save, sender=Product)

post_delete.connect(update_objects_on_product_delete, sender=Product)


class ProductGroupItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='product_groups')
    group = models.ForeignKey(ProductGroup)

    class Meta:
        unique_together = ("product", "group")

    def __unicode__(self):
        return self.id


def update_product_groups_on_save(sender, instance, created, **kwargs):
    if created and instance.group.parent:

        exist = ProductGroupItem.objects.filter(product=instance.product,
                                                group=instance.group.parent).exists()
        if not exist:
            object = ProductGroupItem(product=instance.product, group=instance.group.parent)
            object.save()


post_save.connect(update_product_groups_on_save, sender=ProductGroupItem)


class ProductImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='images')
    image = models.ForeignKey(UserImage, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=80, null=True, blank=True)
    description = models.CharField(max_length=350, null=True, blank=True)
    position = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.position is None:
            try:
                max_position = self.objects.filter(product=self.product).aggregate(Max("position"))
                self.position = (max_position.get("position__max") or 0) + 1
            except:
                self.position = 1
        return super(ProductImage, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
    def __unicode__(self):
        return self.id


def delete_product_img_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete()


post_delete.connect(delete_product_img_on_delete, sender=ProductImage)


class ProductCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='product_categories')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def check_seo_data(self):
        if self.category:
            if self.product.company:
                country = self.product.company.country
                city = self.product.company.city
            else:
                country = self.product.user.user_profile.country
                city = self.product.user.user_profile.city

            check_seo_data_exists(self.category, None, None)
            if country:
                check_seo_data_exists(self.category, country, None)
            if city:
                check_seo_data_exists(self.category, country, city)

    class Meta:
        unique_together = ("product", "category")

    def __unicode__(self):
        return self.id


def update_product_categories_on_save(sender, instance, created, **kwargs):
    if created:
        instance.category.contents_exist('product')
        instance.check_seo_data()
        if instance.category.parent:

            exist = ProductCategory.objects.filter(product=instance.product,
                                                   category=instance.category.parent).exists()
            if not exist:
                object = ProductCategory(product=instance.product, category=instance.category.parent)
                object.save()


post_save.connect(update_product_categories_on_save, sender=ProductCategory)


class ProductAttribute(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, related_name='attributes', null=True, blank=True)
    attribute = models.ForeignKey(Attribute, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=40, null=True, blank=True)
    user_attribute = models.BooleanField(default=True)
    multiple = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id


class ProductAttributeValue(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_attribute = models.ForeignKey(ProductAttribute, related_name='values')
    value_string = models.CharField(max_length=150, blank=True, null=True)
    value_number = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    value_integer = models.IntegerField(null=True, blank=True)
    value_boolean = models.BooleanField(default=False, blank=True)
    value_list = models.ForeignKey(AttributeValue, blank=True, null=True)

    def __unicode__(self):
        return self.id


class FavoriteProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, blank=False, related_name='favorites_products')
    product = models.ForeignKey(Product, related_name='favorites')

    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __unicode__(self):
        return self.id


def update_profile_eventsqty_on_favorite_post_save(sender, instance, created, **kwargs):
    if created:
        instance.user.user_profile.eventsqty.update_events_qty('favorite_products', 1)


def update_profile_eventsqty_on_favorite_post_delete(sender, instance, **kwargs):
    instance.user.user_profile.eventsqty.update_events_qty('favorite_products', -1)


post_save.connect(update_profile_eventsqty_on_favorite_post_save, sender=FavoriteProduct)
post_delete.connect(update_profile_eventsqty_on_favorite_post_delete, sender=FavoriteProduct)


def check_seo_data_exists(category, country,
                          city):
    filter_list = Q()
    if category:
        filter_list = filter_list & Q(category=category)
    else:
        filter_list = filter_list & Q(category__isnull=True)

    if country:
        filter_list = filter_list & Q(country=country)
    else:
        filter_list = filter_list & Q(country__isnull=True)
    if city:
        filter_list = filter_list & Q(city=city)
    else:
        filter_list = filter_list & Q(city__isnull=True)

    exists = ProductSEOData.objects.filter(filter_list).exists()

    if not exists:
        obj = ProductSEOData(category=category, country=country, city=city)
        obj.save()


class ProductSEOData(models.Model):
    category = models.ForeignKey(Category, blank=True, null=True, default=None, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, blank=True, null=True, default=None, on_delete=models.CASCADE)
    city = models.ForeignKey(City, blank=True, null=True, default=None, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def get_absolute_url(self):

        url = '/products'
        lang = translation.get_language()

        url = url + '/' + lang
        url = url + '?'

        if self.country:
            url = url + 'country=' + self.country.slug
        if self.city:
            if self.country:
                url = url + '&'
            url = url + 'city=' + self.city.slug
        if self.category:
            if self.country or self.city:
                url = url + '&'
            url = url + 'category=' + self.category.slug

        return url

    class Meta:
        unique_together = ("category", "country", "city")

    def __unicode__(self):
        return self.id


def update_product_on_suggested_category_processed(sender, instance, **kwargs):
    if instance.pk and instance.reviewed:
        old_instance = SuggestedCategory.objects.get(pk=instance.pk)
        if not old_instance.reviewed:
            products = Product.objects.language('en').filter(suggested_category=instance.id)
            for product in products:
                if instance.category:
                    product.category = instance.category
                    product.suggested_category = None
                    product.save()


pre_save.connect(update_product_on_suggested_category_processed, sender=SuggestedCategory)
