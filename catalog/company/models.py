from __future__ import unicode_literals

from django.db import models
from hvad.models import TranslatableModel, TranslatedFields
from django.db.models.signals import post_delete, post_save, pre_save
from autoslug import AutoSlugField
from unidecode import unidecode

from django.contrib.auth.models import User
from catalog.general.models import Country, City
from catalog.file.models import UserImage
from catalog.user_profile.models import UserProfile
from catalog.category.models import Category
from stream_django.feed_manager import feed_manager
from stream.exceptions import DoesNotExistException
from taggit.managers import TaggableManager
from django.core.exceptions import ObjectDoesNotExist
from hvad.utils import get_translation
from django.conf import settings
from catalog.getstream.utils import create_notification_by_instance, follow_target_feed, unfollow_target_feed
from django.db.models import Q
from django.utils import translation
from catalog.utils.model_mixins import UpdateQtyMixin


class CompanyType(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )

    position = models.IntegerField(default=0)
    slug = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        ordering = ["position"]

    def __unicode__(self):
        return self.id


class CompanySize(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )
    position = models.IntegerField(default=0)
    slug = models.CharField(max_length=60, null=True, blank=True)

    class Meta:
        ordering = ["position"]

    def __unicode__(self):
        return self.id


class CompanyIndustry(TranslatableModel):
    translations = TranslatedFields(
        name=models.CharField(max_length=60)
    )
    slug = models.CharField(max_length=60, null=True, blank=True, unique=True, db_index=True)

    def __unicode__(self):
        return self.id


class IndustryClassification(models.Model):
    slug = models.CharField(max_length=60, null=True, blank=True, unique=True)
    name_en = models.CharField(max_length=60)
    name_ru = models.CharField(max_length=60)
    name_uk = models.CharField(max_length=60)

    def __unicode__(self):
        return self.id


class Company(TranslatableModel):
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    slug = AutoSlugField(populate_from=unidecode('name'), editable=True, blank=True, unique=True)
    logo = models.ForeignKey(UserImage, null=True, blank=True, on_delete=models.SET_NULL)
    website = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    company_industry = models.ForeignKey(CompanyIndustry, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    company_type = models.ForeignKey(CompanyType, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)
    company_size = models.ForeignKey(CompanySize, null=True, blank=True, on_delete=models.SET_NULL, db_index=True)

    address = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=25, null=True, blank=True)
    sales_email = models.CharField(max_length=50, null=True, blank=True)
    business_email = models.CharField(max_length=50, null=True, blank=True)
    foundation_year = models.CharField(max_length=4, null=True, blank=True)
    tags = TaggableManager(blank=True)
    deleted = models.BooleanField(default=False, blank=True)

    translations = TranslatedFields(
        name=models.CharField(max_length=150),
        short_description=models.TextField(null=True, blank=True),
        headline=models.CharField(max_length=150, null=True, blank=True),
        seo_title=models.CharField(max_length=150, null=True, blank=True),
        seo_description=models.CharField(max_length=400, null=True, blank=True),
    )
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, db_index=True)

    def get_absolute_url(self):

        url = '/company/' + self.slug

        url = url + '/' + self.language_code

        return url

    @property
    def activity_object_serializer_class(self):
        from .serializers import CompanySerializer

        return CompanySerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import CompanySmallSerializer

        return CompanySmallSerializer

    def get_email_dict(self, lang):
        try:
            trans = get_translation(self, lang)
        except ObjectDoesNotExist:
            trans = get_translation(self, 'en')
        headline = trans.headline
        name = trans.name
        url = settings.FRONTEND_URL + 'company/' + self.slug
        if self.logo:
            image = self.logo.file.url
        else:
            image = settings.FRONTEND_URL + 'static/assets/img/company-default.png'

        res = dict()
        res['name'] = name
        res['url'] = url
        res['image'] = image
        res['headline'] = headline

        return res

    def smart_delete(self):
        company = self
        company.deleted = True
        company.logo = None
        company.slug = 'company-deleted' + str(company.id)
        company.save()
        company_categories = company.categories
        company_categories.all().delete()
        favorites = company.favorites
        favorites.all().delete()
        communities = company.communities
        communities.all().delete()
        followers = company.followers
        followers.all().delete()

        invitations = company.invitations
        invitations.all().delete()

        try:
            products = company.company_products
            for product in products.all():
                product.smart_delete()

        except ObjectDoesNotExist:
            pass

        try:
            posts = company.company_posts
            for post in posts.all():
                post.smart_delete()

        except ObjectDoesNotExist:
            pass

        try:
            posts = company.company_reviews
            for post in posts.all():
                post.smart_delete()
        except ObjectDoesNotExist:
            pass

        users = company.users
        users.all().delete()

    def _get_name_all_languages(self):
        translations = Company.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.name)
        return values

    def _get_description_all_languages(self):
        translations = Company.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.short_description)
        return values

    def _get_headline_all_languages(self):
        translations = Company.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.headline)
        return values

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
        except CompanyEventsQty.DoesNotExist:
            pass

    name_all_languages = property(_get_name_all_languages)
    description_all_languages = property(_get_description_all_languages)
    headline_all_languages = property(_get_headline_all_languages)

    @property
    def tags_indexing(self):

        return [tag.name for tag in self.tags.all()]

    @property
    def categories_indexing(self):

        values = []
        for category in self.categories.all():
            values.append(category.category_id)
        return values

    @property
    def location_field_indexing(self):

        if (self.city):
            return {
                'lat': self.city.latitude,
                'lon': self.city.longitude,
            }
        else:
            return {'lat': 0, 'lon': 0}

    def check_seo_data(self):
        if self.country:
            check_seo_data_exists(None, self.country, None, None, None)
        if self.city:
            check_seo_data_exists(None, self.country, self.city, None, None)
        if self.company_type:
            check_seo_data_exists(None, None, None, self.company_type, None)
        if self.company_industry:
            check_seo_data_exists(None, None, None, None, self.company_industry)

        if self.company_type and self.country:
            check_seo_data_exists(None, self.country, None, self.company_type, None)
        if self.company_type and self.city:
            check_seo_data_exists(None, self.country, self.city, self.company_type, None)

        if self.company_industry and self.country:
            check_seo_data_exists(None, self.country, None, None, self.company_industry)
        if self.company_industry and self.city:
            check_seo_data_exists(None, self.country, self.city, None, self.company_industry)

        if self.company_type and self.company_industry and self.country:
            check_seo_data_exists(None, self.country, None, self.company_type, self.company_industry)
        if self.company_type and self.company_industry and self.city:
            check_seo_data_exists(None, self.country, self.city, self.company_type, self.company_industry)

    def __unicode__(self):
        return self.id


def update_general_info_on_company_save(sender, instance, created, **kwargs):
    if instance.country:
        if not instance.country.companies_exist:
            instance.country.companies_exist = True
            instance.country.save()
    if instance.city:
        if not instance.city.companies_exist:
            instance.city.companies_exist = True
            instance.city.save()

    instance.check_seo_data()

    # for category in instance.categories.all():
    #     check_category_country(category.category, instance.country)
    #     check_category_city(category.category, instance.city)

    if created:
        object = CompanyEventsQty(company=instance)
        object.save()


post_save.connect(update_general_info_on_company_save, sender=Company)


def delete_company_logo_on_save(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Company.objects.get(pk=instance.pk)
        if old_instance.logo and old_instance.logo != instance.logo:
            old_instance.logo.delete()


def delete_company_logo_on_delete(sender, instance, **kwargs):
    if instance.logo:
        instance.logo.delete()


pre_save.connect(delete_company_logo_on_save, Company)
post_delete.connect(delete_company_logo_on_delete, sender=Company)


class CompanyEventsQty(UpdateQtyMixin ,models.Model):
    company = models.OneToOneField(Company, related_name='eventsqty', primary_key=True)
    followers = models.PositiveIntegerField(default=0, db_index=True)
    employees = models.PositiveIntegerField(default=0)
    students = models.PositiveIntegerField(default=0)
    jobposts = models.PositiveIntegerField(default=0)
    publications = models.PositiveIntegerField(default=0)
    offerings = models.PositiveIntegerField(default=0)
    requests = models.PositiveIntegerField(default=0)
    new_messages = models.PositiveIntegerField(default=0)

    new_job_responds = models.PositiveIntegerField(default=0)
    new_offering_reponds = models.PositiveIntegerField(default=0)
    new_request_responds = models.PositiveIntegerField(default=0)
    new_customer_requests = models.PositiveIntegerField(default=0)
    open_customer_requests = models.PositiveIntegerField(default=0)
    your_open_supply_requests = models.PositiveIntegerField(default=0)
    your_open_offering_responds = models.PositiveIntegerField(default=0)
    your_open_request_responds = models.PositiveIntegerField(default=0)

    products = models.PositiveIntegerField(default=0)
    reviews = models.PositiveIntegerField(default=0)
    questions = models.PositiveIntegerField(default=0)
    related_reviews = models.PositiveIntegerField(default=0, db_index=True)
    related_questions = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1, db_index=True)

    def __unicode__(self):
        return self.id


class CompanyUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='managed_companies', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='users', on_delete=models.CASCADE)
    admin = models.BooleanField(default=False)
    sales = models.BooleanField(default=False)
    supply = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "user")

    def __unicode__(self):
        return self.id


def company_user_notification(sender, instance, created, **kwargs):
    if created and instance.admin is True:
        profile = UserProfile.objects.language().fallbacks('en').get(id=instance.user.user_profile.id)
        profile.has_companies = True
        profile.save()
        create_notification_by_instance(instance, 'administrator_created')


def company_user_notification_on_delete(sender, instance, **kwargs):
    if instance.admin is True:
        companies_exist = CompanyUser.objects.filter(user=instance.user, admin=True).exists()
        if not companies_exist:
            profile = UserProfile.objects.language('en').get(pk=instance.user.user_profile.id)
            profile.has_companies = False
            profile.save()
        create_notification_by_instance(instance, 'administrator_deleted')


post_save.connect(company_user_notification, sender=CompanyUser)
post_delete.connect(company_user_notification_on_delete, sender=CompanyUser)


class CompanyCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, related_name='categories')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    child_qty = models.IntegerField(default=0)
    products_qty = models.IntegerField(default=0)
    interest = models.BooleanField(default=True)  # True - interest; False - offer
    company_category = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def check_seo_data(self):
        if self.category:
            if self.company.country:
                check_seo_data_exists(self.category, self.company.country, None, None, None)
            if self.company.city:
                check_seo_data_exists(self.category, self.company.country, self.company.city, None, None)
            if self.company.company_type:
                check_seo_data_exists(self.category, None, None, self.company.company_type, None)
            if self.company.company_industry:
                check_seo_data_exists(self.category, None, None, None, self.company.company_industry)

            if self.company.company_type and self.company.country:
                check_seo_data_exists(self.category, self.company.country, None, self.company.company_type, None)
            if self.company.company_type and self.company.city:
                check_seo_data_exists(self.category, self.company.country, self.company.city, self.company.company_type,
                                      None)

            if self.company.company_industry and self.company.country:
                check_seo_data_exists(self.category, self.company.country, None, None, self.company.company_industry)
            if self.company.company_industry and self.company.city:
                check_seo_data_exists(self.category, self.company.country, self.company.city, None,
                                      self.company.company_industry)

            if self.company.company_type and self.company.company_industry and self.company.country:
                check_seo_data_exists(self.category, self.company.country, None, self.company.company_type,
                                      self.company.company_industry)
            if self.company.company_type and self.company.company_industry and self.company.city:
                check_seo_data_exists(self.category, self.company.country, self.company.city, self.company.company_type,
                                      self.company.company_industry)

    class Meta:
        unique_together = ("company", "category", 'interest')

    def __unicode__(self):
        return "%s  %s  %s" % (self.id, self.company, self.category)


def update_company_categories_on_delete(sender, instance, **kwargs):
    if instance.category.parent:
        try:
            object = CompanyCategory.objects.get(company=instance.company, category=instance.category.parent,
                                                 interest=instance.interest)

            if object.child_qty <= 1 and object.products_qty == 0:
                object.delete()

            else:
                if object.child_qty >= 1:
                    object.child_qty = object.child_qty - 1
                    object.save()


        except:
            pass


def update_company_categories_on_save(sender, instance, created, **kwargs):
    if created and instance.category.parent:

        exist = CompanyCategory.objects.filter(company=instance.company,
                                               category=instance.category.parent,
                                               interest=instance.interest).exists()
        if not exist:
            object = CompanyCategory(company=instance.company, category=instance.category.parent,
                                     interest=instance.interest, child_qty=1)
            object.save()
        else:
            parent = CompanyCategory.objects.get(company=instance.company,
                                                 category=instance.category.parent,
                                                 interest=instance.interest)
            qty = CompanyCategory.objects.filter(company=instance.company, interest=instance.interest,
                                                 category__parent=parent.category).count()
            if qty:
                parent.child_qty = qty
            else:
                parent.child_qty = 0
            parent.save()

    if created:
        instance.category.contents_exist('company')
        instance.check_seo_data()
        # check_category_country(instance.category, instance.company.country)
        # if instance.company.city:
        #     check_category_city(instance.category, instance.company.city)


post_save.connect(update_company_categories_on_save, sender=CompanyCategory)
post_delete.connect(update_company_categories_on_delete, sender=CompanyCategory)


class CompanyFollower(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='following_companies', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='followers', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("company", "user")

    def __unicode__(self):
        return self.id



def follow_company_feed(sender, instance, created, **kwargs):
    follow_target_feed('company', instance.user.id, instance.company.id)


def unfollow_company_feed(sender, instance, **kwargs):
    unfollow_target_feed('company', instance.user.id, instance.company.id)



def update_user_feed_on_follow(sender, instance, created, **kwargs):
    if created:
        instance.company.eventsqty.update_events_qty('followers', 1)
        feed_name = 'user'
        feed = feed_manager.get_feed(feed_name, instance.user.id)
        actor = 'auth.User:' + str(instance.user.id)
        activity_data = {'actor': actor, 'verb': 'company_follower',
                         'object': 'company.CompanyFollower:' + str(instance.id),
                         'target': 'company.Company:' + str(instance.company.id),
                         'foreign_id': 'company.CompanyFollower:' + str(instance.id), 'time': instance.create_date}

        feed.add_activity(activity_data)
        create_notification_by_instance(instance, 'new_follower')


def update_user_feed_on_unfollow(sender, instance, **kwargs):
    instance.company.eventsqty.update_events_qty('followers', -1)
    feed_name = 'user'
    feed = feed_manager.get_feed(feed_name, instance.user.id)
    try:
        feed.remove_activity(foreign_id='company.CompanyFollower:' + str(instance.id))
    except DoesNotExistException:
        pass


post_save.connect(follow_company_feed, sender=CompanyFollower)
post_delete.connect(unfollow_company_feed, sender=CompanyFollower)
post_save.connect(update_user_feed_on_follow, sender=CompanyFollower)
post_delete.connect(update_user_feed_on_unfollow, sender=CompanyFollower)


class FavoriteCompany(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, blank=False, related_name='favorites_companies', on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='favorites', on_delete=models.CASCADE)

    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "company")

    def __unicode__(self):
        return self.id


def update_profile_eventsqty_on_favorite_post_save(sender, instance, created, **kwargs):
    if created:
        instance.user.user_profile.eventsqty.update_events_qty('favorite_companies', 1)


def update_profile_eventsqty_on_favorite_post_delete(sender, instance, **kwargs):
    instance.user.user_profile.eventsqty.update_events_qty('favorite_companies', -1)


post_save.connect(update_profile_eventsqty_on_favorite_post_save, sender=FavoriteCompany)
post_delete.connect(update_profile_eventsqty_on_favorite_post_delete, sender=FavoriteCompany)


def check_seo_data_exists(category, country,
                          city, company_type,
                          company_industry):
    filter_list = Q()
    if category:
        filter_list = filter_list & Q(category=category)
    else:
        filter_list = filter_list & Q(category__isnull=True)
    if company_type:
        filter_list = filter_list & Q(company_type=company_type)
    else:
        filter_list = filter_list & Q(company_type__isnull=True)
    if country:
        filter_list = filter_list & Q(country=country)
    else:
        filter_list = filter_list & Q(country__isnull=True)
    if city:
        filter_list = filter_list & Q(city=city)
    else:
        filter_list = filter_list & Q(city__isnull=True)
    if company_industry:
        filter_list = filter_list & Q(company_industry=company_industry)
    else:
        filter_list = filter_list & Q(company_industry__isnull=True)

    exists = CompanySEOData.objects.filter(filter_list).exists()

    if not exists:
        obj = CompanySEOData(category=category, company_type=company_type, country=country, city=city,
                             company_industry=company_industry)
        obj.save()


class CompanySEOData(models.Model):
    category = models.ForeignKey(Category, blank=True, null=True, default=None, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, blank=True, null=True, default=None, on_delete=models.CASCADE)
    city = models.ForeignKey(City, blank=True, null=True, default=None, on_delete=models.CASCADE)
    company_type = models.ForeignKey(CompanyType, blank=True, null=True, default=None, on_delete=models.CASCADE)
    company_industry = models.ForeignKey(CompanyIndustry, blank=True, null=True, default=None, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def get_absolute_url(self):
        url = '/companies'
        lang = translation.get_language()

        url = url + '/' + lang
        url = url + '?'

        is_attributes = False
        if self.country:
            url = url + 'country=' + self.country.slug
            is_attributes = True
        if self.city:
            if is_attributes:
                url = url + '&'
            url = url + 'city=' + self.city.slug
            is_attributes = True
        if self.category:
            if is_attributes:
                url = url + '&'
            url = url + 'category=' + self.category.slug
            is_attributes = True
        if self.company_industry:
            if is_attributes:
                url = url + '&'
            url = url + 'company_industry=' + self.company_industry.slug
            is_attributes = True
        if self.company_type:
            if is_attributes:
                url = url + '&'
            url = url + 'company_type=' + self.company_type.slug

        return url

    class Meta:
        unique_together = ("category", "country", "city", "company_type", "company_industry")

    def __unicode__(self):
        return self.id
