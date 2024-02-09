from __future__ import unicode_literals
from catalog.general.models import Language, Country, City, Currency

from django.contrib.auth.models import User
from django.db import models
from catalog.file.models import UserImage
from catalog.category.models import Category
from catalog.file.models import File
from django.db.models.signals import post_delete, post_save, pre_save
from autoslug import AutoSlugField
from unidecode import unidecode
from hvad.models import TranslatableModel, TranslatedFields, TranslationManager
from taggit.managers import TaggableManager
from django.db import IntegrityError
from django.utils.translation import get_language
from django.core.exceptions import ObjectDoesNotExist
from hvad.utils import get_translation
from django.conf import settings
from catalog.getstream.utils import create_notification_by_instance, follow_target_feed, unfollow_target_feed
from catalog.utils.model_mixins import UpdateQtyMixin


class UserProfileManager(TranslationManager):
    def get_or_create_for_cognito(self, payload):

        cognito_id = payload['cognito:username']

        try:
            user = User.objects.get(username=cognito_id)
        except User.DoesNotExist:
            try:

                name = payload['name']
                try:
                    family_name = payload['family_name']
                except:
                    family_name = ''
                email = payload['email']
                user = User(
                    username=cognito_id, first_name=name, last_name=family_name, email=email,
                    is_active=True)
                user.save()
            except IntegrityError:
                user = User.objects.get(username=cognito_id)

        return user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            try:
                locale = get_language()
                language = Language.objects.get(code=locale)
            except Language.DoesNotExist:
                language = Language.objects.get(code='en')

            profile = UserProfile(user=instance, email=instance.email, first_name=instance.first_name,
                                  last_name=instance.last_name, nickname=instance.first_name + instance.last_name,
                                  interface_lang=language, language_code='en')
            profile.save()


        except IntegrityError:
            pass


post_save.connect(create_user_profile, sender=User)


class UserProfile(TranslatableModel):
    objects = UserProfileManager()

    id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE)
    interface_lang = models.ForeignKey(Language, blank=True, null=True, on_delete=models.SET_NULL)
    has_companies = models.BooleanField(default=False, blank=True)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL, db_index=True)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.SET_NULL, db_index=True)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    default_currency = models.ForeignKey(Currency, null=True, default=1, on_delete=models.SET_NULL)
    img = models.ForeignKey(UserImage, blank=True, null=True, on_delete=models.SET_NULL)
    email = models.CharField(max_length=100, null=True, blank=True)
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    skype = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    nickname = models.CharField(max_length=225, null=True, blank=True)
    slug = AutoSlugField(populate_from=unidecode('nickname'), editable=True, unique=True)
    job_title = models.CharField(max_length=150, blank=True, null=True)
    tags = TaggableManager(blank=True)
    deleted = models.BooleanField(default=False, blank=True)
    translations = TranslatedFields(
        first_name=models.CharField(max_length=60, null=True, blank=True),
        last_name=models.CharField(max_length=60, null=True, blank=True),
        full_name=models.CharField(max_length=120, null=True, blank=True, db_index=True),
        short_description=models.TextField(null=True, blank=True),
        headline=models.CharField(max_length=150, null=True, blank=True)
    )
    settings_checked = models.BooleanField(default=False)
    notifications_sound = models.BooleanField(default=True)
    message_sound = models.BooleanField(default=True)
    notifications_email = models.BooleanField(default=True)
    message_email = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, db_index=True)
    tester = models.BooleanField(default=False, blank=True)

    def get_absolute_url(self):

        url = '/user-profile/' + self.slug
        url = url + '/' + self.language_code

        return url

    @property
    def activity_object_serializer_class(self):
        from .serializers import UserProfileShortSerializer

        return UserProfileShortSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import UserProfileShortSerializer

        return UserProfileShortSerializer

    def get_email_dict(self, lang):
        url = settings.FRONTEND_URL + 'user-profile/' + self.slug

        try:
            trans = get_translation(self, lang)
        except ObjectDoesNotExist:
            trans = get_translation(self, 'en')

        name = trans.first_name + ' ' + trans.last_name

        headline = trans.headline

        if self.img:
            image = self.img.file.url
        else:
            image = settings.FRONTEND_URL + 'static/assets/img/default-user.jpeg'

        res = dict()
        res['name'] = name
        res['url'] = url
        res['image'] = image
        res['headline'] = headline

        return res

    def smart_delete(self):

        translations = UserProfile.objects.language('all').filter(pk=self.pk)

        for translation in translations:
            translation.first_name = 'А user is deleted'
            translation.last_name = None
            translation.short_description = None
            translation.headline = None
            translation.save()

        profile = self
        profile.deleted = True
        profile.img = None
        profile.contact_email = None
        profile.contact_phone = None
        profile.email = None
        profile.website = None
        profile.slug = 'user-deleted' + str(profile.id)
        profile.nickname = None
        profile.save()

        profile_categories = profile.user_categories
        profile_categories.all().delete()
        user_country_interest = profile.user_country_interest
        user_country_interest.all().delete()
        followers = profile.followers
        followers.all().delete()
        following_profiles = profile.user.following_profiles
        following_profiles.all().delete()
        following_companies = profile.user.following_companies
        following_companies.all().delete()
        employment = profile.employment
        employment.all().delete()
        managed_companies = profile.user.managed_companies
        managed_companies.all().delete()
        communities = profile.user.communities
        communities.all().delete()
        invitations = profile.user.invitations
        invitations.all().delete()
        resumes = profile.resumes
        resumes.all().delete()

        try:
            products = profile.user.user_products.filter(company__isnull=True)
            for product in products.all():
                product.smart_delete()

        except ObjectDoesNotExist:
            pass

        try:
            posts = profile.user.user_posts.filter(company__isnull=True)
            for post in posts.all():
                post.smart_delete()

        except ObjectDoesNotExist:
            pass

        try:
            posts = profile.user.user_reviews
            for post in posts.all():
                post.smart_delete()
        except ObjectDoesNotExist:
            pass

        likes = profile.user.likes
        likes.all().delete()
        comments = profile.user.comments
        comments.all().delete()
        comments_on_posts = profile.user.comments_on_posts
        comments_on_posts.all().delete()

    def _get_is_active(self):
        return self.user.is_active

    def _get_name_all_languages(self):
        translations = UserProfile.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            str = None
            if translation.first_name:
                str = translation.first_name
            if translation.last_name:
                str = str + ' ' + translation.last_name
            if str is not None:
                values.append(str)
        return values

    def _get_description_all_languages(self):
        translations = UserProfile.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.short_description)
        return values

    def _get_headline_all_languages(self):
        translations = UserProfile.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.headline)
        return values

    def _get_employment_all_languages(self):
        employments = self.employment.all()
        values = []
        for employment in employments:
            employment_values = employment.name_all_languages
            values.extend(employment_values)
            employment_values = employment.description_all_languages
            values.extend(employment_values)
        return values

    @property
    def tags_indexing(self):

        """Tags for indexing.

              Used in Elasticsearch indexing.

                  """
        profile = UserProfile.objects.language('en').get(pk=self.id)
        values = []
        if profile.tags:
            for tag in profile.tags.all():
                values.append(tag.name)
        return values

    @property
    def categories_indexing(self):
        """Tags for indexing.

        Used in Elasticsearch indexing.
        """

        values = []
        for category in self.user_categories.filter(interest=False):
            values.append(category.category_id)
        return values

    @property
    def company_industry_indexing(self):
        """Tags for indexing.

        Used in Elasticsearch indexing.
        """

        values = []
        for employment in self.employment.all():
            if (employment.company):
                if (employment.company.company_industry):
                    values.append(employment.company.company_industry.id)
        return values

    @property
    def company_type_indexing(self):
        """Tags for indexing.

        Used in Elasticsearch indexing.
        """

        values = []
        for employment in self.employment.all():
            if (employment.company):
                if (employment.company.company_type):
                    values.append(employment.company.company_type.id)
        return values

    @property
    def company_size_indexing(self):
        """Tags for indexing.

        Used in Elasticsearch indexing.
        """

        values = []
        for employment in self.employment.all():
            if (employment.company):
                if (employment.company.company_size):
                    values.append(employment.company.company_size.id)
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
        except UserProfileEventsQty.DoesNotExist:
            pass


    is_active = property(_get_is_active)
    name_all_languages = property(_get_name_all_languages)
    description_all_languages = property(_get_description_all_languages)
    headline_all_languages = property(_get_headline_all_languages)
    employment_all_languages = property(_get_employment_all_languages)

    def save(self, *args, **kwargs):
        if not self.deleted:
            first_name = ''
            last_name = ''

            if self.first_name:
                first_name = self.first_name
            if self.last_name:
                last_name = self.last_name

            self.full_name = first_name + ' ' + last_name
        return super(UserProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.email


def update_general_info_on_profile_save(sender, instance, created, **kwargs):
    if instance.country:
        if not instance.country.users_exist:
            instance.country.users_exist = True
            instance.country.save()
    if instance.city:
        if not instance.city.users_exist:
            instance.city.users_exist = True
            instance.city.save()

    if created:
        object = UserProfileEventsQty(profile=instance)
        object.save()


post_save.connect(update_general_info_on_profile_save, sender=UserProfile)


def check_profile_on_save(sender, instance, **kwargs):
    if instance.pk:
        old_instance = UserProfile.objects.get(pk=instance.pk)
        if old_instance.img and old_instance.img != instance.img:
            old_instance.img.delete()

        if not old_instance.settings_checked and instance.settings_checked:
            welcome = UserAction(user=instance.user, code='welcome')
            welcome.save()


def delete_profile_img_on_delete(sender, instance, **kwargs):
    if instance.img:
        instance.img.delete()


pre_save.connect(check_profile_on_save, UserProfile)
post_delete.connect(delete_profile_img_on_delete, sender=UserProfile)




class UserProfileEventsQty(UpdateQtyMixin, models.Model):
    profile = models.OneToOneField(UserProfile, related_name='eventsqty', primary_key=True, on_delete=models.CASCADE)
    following = models.PositiveIntegerField(default=0)
    followers = models.PositiveIntegerField(default=0, db_index=True)
    jobposts = models.PositiveIntegerField(default=0)
    publications = models.PositiveIntegerField(default=0)
    offerings = models.PositiveIntegerField(default=0)
    requests = models.PositiveIntegerField(default=0)
    products = models.PositiveIntegerField(default=0)
    notifications = models.PositiveIntegerField(default=0)
    new_messages = models.PositiveIntegerField(default=0)
    new_job_responds = models.PositiveIntegerField(default=0)
    new_offering_reponds = models.PositiveIntegerField(default=0)
    new_request_responds = models.PositiveIntegerField(default=0)
    new_customer_requests = models.PositiveIntegerField(default=0)
    open_customer_requests = models.PositiveIntegerField(default=0)
    your_open_supply_requests = models.PositiveIntegerField(default=0)
    your_open_offering_responds = models.PositiveIntegerField(default=0)
    your_open_request_responds = models.PositiveIntegerField(default=0)
    your_open_job_responds = models.PositiveIntegerField(default=0)
    favorite_posts = models.PositiveIntegerField(default=0)
    favorite_companies = models.PositiveIntegerField(default=0)
    favorite_products = models.PositiveIntegerField(default=0)
    favorite_communities = models.PositiveIntegerField(default=0)
    favorite_tags = models.PositiveIntegerField(default=0)
    reviews = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(default=0, max_digits=2, decimal_places=1, db_index=True)
    questions = models.PositiveIntegerField(default=0)
    related_questions = models.PositiveIntegerField(default=0)
    related_reviews = models.PositiveIntegerField(default=0, db_index=True)

    def __unicode__(self):
        return self.id


class UserProfileFollower(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='following_profiles', on_delete=models.CASCADE)
    profile = models.ForeignKey(UserProfile, related_name='followers', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "user")

    def __unicode__(self):
        return self.id


def profile_user_notification(sender, instance, created, **kwargs):
    if created:
        create_notification_by_instance(instance, 'new_follower')


post_save.connect(profile_user_notification, sender=UserProfileFollower)


class UserProfileCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    profile = models.ForeignKey(UserProfile, related_name='user_categories', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    child_qty = models.IntegerField(default=0)
    interest = models.BooleanField(default=True)  # True - interest; False - offer
    profile_category = models.BooleanField(default=False)
    products_qty = models.IntegerField(default=0)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("profile", "category", 'interest')

    def __unicode__(self):
        return "%s  %s  %s" % (self.id, self.profile, self.category)


def update_user_categories_on_delete(sender, instance, **kwargs):
    if instance.category.parent:
        try:
            object = UserProfileCategory.objects.get(profile=instance.profile, category=instance.category.parent,
                                                     interest=instance.interest)

            if object.child_qty <= 1 and object.products_qty == 0:
                object.delete()

            else:
                if object.child_qty >= 1:
                    object.child_qty = object.child_qty - 1
                    object.save()


        except:
            pass


def update_user_categories_on_save(sender, instance, created, **kwargs):
    if created and instance.category.parent:

        exist = UserProfileCategory.objects.filter(profile=instance.profile,
                                                   category=instance.category.parent,
                                                   interest=instance.interest).exists()
        if not exist:
            object = UserProfileCategory(profile=instance.profile, category=instance.category.parent,
                                         interest=instance.interest, child_qty=1)
            object.save()
        else:
            parent = UserProfileCategory.objects.get(profile=instance.profile,
                                                     category=instance.category.parent,
                                                     interest=instance.interest)
            qty = UserProfileCategory.objects.filter(profile=instance.profile, interest=instance.interest,
                                                     category__parent=parent.category).count()
            if qty:
                parent.child_qty = qty
            else:
                parent.child_qty = 0
            parent.save()

    if created and instance.interest == False:
        instance.category.contents_exist('user')


post_save.connect(update_user_categories_on_save, sender=UserProfileCategory)
post_delete.connect(update_user_categories_on_delete, sender=UserProfileCategory)


class UserProfileCountryInterest(models.Model):
    id = models.BigAutoField(primary_key=True)
    profile = models.ForeignKey(UserProfile, related_name='user_country_interest')
    country = models.ForeignKey(Country)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "country")

    def __unicode__(self):
        return "%s  %s  %s" % (self.id, self.profile, self.country)


def follow_user_feed(instance):
    """
    following feeds of a new user profile
    """
    follow_target_feed('user', instance.user.id, instance.profile.user.id)


def unfollow_user_feed(instance):
    """
    Unfollow feeds of a user profile
    """

    unfollow_target_feed('user', instance.user.id, instance.profile.user.id)


def follow_feed_on_user_follower_save(sender, instance, created, **kwargs):
    if created:
        follow_user_feed(instance)
        instance.profile.eventsqty.update_events_qty('followers', 1)
        instance.user.user_profile.eventsqty.update_events_qty('following', 1)


def unfollow_feed_on_user_follower_delete(sender, instance, **kwargs):
    unfollow_user_feed(instance)
    instance.profile.eventsqty.update_events_qty('followers', -1)
    instance.user.user_profile.eventsqty.update_events_qty('following', -1)


post_save.connect(follow_feed_on_user_follower_save, sender=UserProfileFollower)
post_delete.connect(unfollow_feed_on_user_follower_delete, sender=UserProfileFollower)


class Resume(models.Model):
    id = models.BigAutoField(primary_key=True)
    profile = models.ForeignKey(UserProfile, related_name='resumes', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    show_in_profile = models.BooleanField(default=False, null=None, blank=None)
    file = models.ForeignKey(File, null=True, on_delete=models.SET_NULL)

    def __unicode__(self):
        return self.id


class UserAction(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='actions', on_delete=models.CASCADE)
    code = models.CharField(max_length=15, db_index=True)
    processed = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id
