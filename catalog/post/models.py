from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from catalog.category.models import Category, SuggestedCategory
from catalog.company.models import Company
from catalog.product.models import Product
from catalog.community.models import Community
from catalog.general.models import Country, UnitType, Currency, City, convert_price, JobType, JobFunction, \
    SeniorityLabel, Language
from catalog.file.models import File, UserImage
from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from hvad.models import TranslatableModel
from catalog.attribute.models import Attribute, AttributeValue
from django.core.exceptions import ObjectDoesNotExist
from taggit.managers import TaggableManager
from taggit.models import TaggedItem
from django.contrib.contenttypes.models import ContentType

from catalog.mention.utils import parse_hashtags
from catalog.getstream.utils import add_feed_activity, delete_activity, \
    create_feed_activity, delete_activity_by_instance, get_update_user_feed_status, create_notification_by_instance
from catalog.messaging.models import Chat, ChatParticipant, create_message
from datetime import datetime
from django.db.models import Q
from django.utils import translation
from hvad.models import TranslatableModel, TranslatedFields
from catalog.utils.utils import truncate_html_description
from catalog.utils.utils import unique_slugify
from catalog.utils.model_mixins import UpdateQtyMixin
from stream_django.client import stream_client
from stream_django.feed_manager import feed_manager


class PostType(TranslatableModel):
    code = models.CharField(max_length=10, null=True, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=40),
        name_plural=models.CharField(max_length=40, null=True, blank=True)
    )
    position = models.IntegerField(null=True, blank=True)

    feed_id = models.IntegerField(null=True, blank=True)
    object_related = models.BooleanField(default=False)

    def __unicode__(self):
        return self.code


class Post(models.Model):
    id = models.BigAutoField(primary_key=True)
    shared_post = models.ForeignKey('self', related_name='child_posts', null=True, blank=True, default=None,
                                    on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='user_posts')
    company = models.ForeignKey(Company, related_name='company_posts', blank=True, null=True, on_delete=models.SET_NULL)
    slug = models.CharField(max_length=500, blank=True, null=True, db_index=True)
    product = models.ForeignKey(Product, related_name='product_posts', blank=True, null=True, on_delete=models.SET_NULL)
    community = models.ForeignKey(Community, related_name='community_posts', blank=True, null=True,
                                  on_delete=models.SET_NULL)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    suggested_category = models.ForeignKey(SuggestedCategory, blank=True, null=True, on_delete=models.SET_NULL)
    related_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                     related_name='user_reviews')
    related_company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL,
                                        related_name='company_reviews')
    related_product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL,
                                        related_name='product_reviews')
    type = models.ForeignKey(PostType, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, blank=True, null=True, on_delete=models.SET_NULL)
    city_name = models.CharField(max_length=100, null=True, blank=True)
    url = models.URLField(blank=True, null=True, max_length=500)
    site_name = models.CharField(blank=True, null=True, max_length=50)
    is_video_url = models.BooleanField(default=False)
    image_url = models.CharField(max_length=350, blank=True, null=True)
    title = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    post_title = models.CharField(max_length=500, blank=True, null=True)
    seo_title = models.CharField(max_length=150, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)
    deadline = models.DateField(null=True, blank=True)
    multi_selection = models.BooleanField(default=False)
    manual_related_posts = models.BooleanField(default=False)
    allow_index = models.BooleanField(default=False)
    post_language = models.CharField(max_length=2, blank=True, null=True)
    promotion = models.BooleanField(default=False, db_index=True)
    promotion_date = models.DateField(null=True, blank=True, db_index=True)
    promotion_grade = models.PositiveIntegerField(default=1, db_index=True)
    prohibited = models.BooleanField(default=False)

    def _get_community_status(self):
        if self.community:
            return self.community.open
        return True

    is_open_community = property(_get_community_status)

    @property
    def categories_indexing(self):
        """Tags for indexing.

        Used in Elasticsearch indexing.
        """

        values = []
        for category in self.post_categories.all():
            values.append(category.category_id)
        return values

    @property
    def activity_object_serializer_class(self):
        from .serializers import PostSerializer
        return PostSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import PostShortSerializer

        return PostShortSerializer

    def create_hashtags(self):
        if self.comment:
            hashtag_set = parse_hashtags(self.comment)
            self.tags.set(*hashtag_set, clear=False)

    def smart_delete(self):
        self.delete_all_feed()
        self.published = False
        self.deleted = True
        self.post_title = None
        self.comment = None
        self.description = None
        self.title = None
        self.url = None
        self.image_url = None

        filters = self.filters
        filters.all().delete()
        favorites = self.favorites
        favorites.all().delete()
        images = self.images
        images.all().delete()
        documents = self.documents
        documents.all().delete()
        likes = self.likes
        likes.all().delete()
        comments = self.comments
        comments.all().delete()
        commentators = self.commentators
        commentators.all().delete()
        post_categories = self.post_categories
        post_categories.all().delete()

        if self.type.code == 'article':
            try:
                article = self.article

                if article:
                    article.delete()
            except:
                pass

        if self.type.code == 'job':
            try:
                post_job = self.post_job

                if post_job:
                    post_job.delete()
            except:
                pass

        self.save()

    def delete_all_feed(self):

        filters = self.filters
        for filter_obj in filters.all():
            delete_activity_by_instance(filter_obj)

        post_likes = self.likes

        for like in post_likes.all():
            delete_activity_by_instance(like)

        post_comments = self.comments

        for comment in post_comments.all():
            delete_activity_by_instance(comment)

        ct = ContentType.objects.get(app_label="post", model="post")
        tags = TaggedItem.objects.filter(object_id=self.id, content_type_id=ct.id)
        for tag in tags.all():
            remove_tag_feed(self, tag.tag_id, tag.id)

        shared_posts = self.child_posts
        for shared_post in shared_posts.all():
            shared_post.delete_all_feed()

        delete_activity_by_instance(self)

    def create_feed(self, create_tags=False):

        create_feed_activity(self)
        # add_post_activity(self)

        if create_tags:
            ct = ContentType.objects.get(app_label="post", model="post")
            tags = TaggedItem.objects.filter(object_id=self.id, content_type_id=ct.id)
            for tag in tags.all():
                create_tag_feed(self, tag.tag_id, tag.id)

        if self.category:
            filters = self.filters

            for filter_obj in filters.all():
                create_feed_activity(filter_obj)

    def update_foreign_instances_qty(self, qty):
        code_dic = {"article": "publications", "post": "publications",
                    "offering": "offerings", "request": "requests",
                    "job": "jobposts", "review": "reviews", "question": "questions"}

        product_dic = {"article": "publications", "post": "publications",
                       "offering": "publications", "request": "publications",
                       "job": "publications", "review": "reviews", "question": "questions"}

        if self.type.code in code_dic:
            event_name = code_dic[self.type.code]
            if self.community:
                self.community.eventsqty.update_events_qty(event_name, qty)
            if self.community is None and self.company:
                self.company.eventsqty.update_events_qty(event_name, qty)
            if self.community is None and self.company is None:
                self.user.user_profile.eventsqty.update_events_qty(event_name, qty)
            if self.product:
                product_event = product_dic[self.type.code]
                self.product.eventsqty.update_events_qty(product_event, qty)

        if self.type.code == 'question':
            if self.related_product:
                self.related_product.eventsqty.update_events_qty('related_questions', qty)
            if self.related_user:
                self.related_user.user_profile.eventsqty.update_events_qty('related_questions', qty)
            if self.related_company:
                self.related_company.eventsqty.update_events_qty('related_questions', qty)

        if qty < 0:
            if self.type.code == 'job':
                for application in self.applicants.all():
                    if not application.reviewed:
                        if self.company:
                            self.company.eventsqty.update_events_qty('new_job_responds', -1)
                        else:
                            self.user.user_profile.eventsqty.update_events_qty('new_job_responds', -1)

                    if application.status.code == 'interview' or application.status.code == 'new':
                        application.user.user_profile.eventsqty.update_events_qty('your_open_job_responds', -1)

            if self.type.code == 'offering' or self.type.code == 'request':
                for respond in self.responds.all():
                    if not respond.reviewed:
                        if self.company:
                            if self.type.code == 'offering':
                                self.company.eventsqty.update_events_qty('new_offering_responds', -1)

                            if self.type.code == 'request':
                                self.company.eventsqty.update_events_qty('new_request_responds', -1)
                        else:
                            if self.type.code == 'offering':
                                self.user.user_profile.eventsqty.update_events_qty('new_offering_responds', -1)

                            if self.type.code == 'request':
                                self.user.user_profile.eventsqty.update_events_qty('new_request_responds', -1)

                    if respond.status.code == 'new':
                        if respond.company:
                            if self.type.code == 'offering':
                                respond.company.eventsqty.update_events_qty('new_offering_responds', -1)

                            if self.type.code == 'request':
                                respond.company.eventsqty.update_events_qty('new_request_responds', -1)
                        else:
                            if self.type.code == 'offering':
                                respond.user.user_profile.eventsqty.update_events_qty('new_offering_responds_qty', -1)

                            if self.type.code == 'request':
                                respond.user.user_profile.eventsqty.update_events_qty('new_request_responds', -1)

    def create_filter_feed(self, filter_id):
        if self.type and filter_id and self.category:
            PostFilterFeed.objects.get_or_create(post=self, filter_id=filter_id)

    def check_seo_data(self):
        if self.category:
            if self.type:
                check_seo_data_exists(None, self.type, None, None, None, None, None)
            if self.country:
                check_seo_data_exists(None, None, self.country, None, None, None, None)

            if self.city:
                check_seo_data_exists(None, None, self.country, self.city, None, None, None)

            if self.type and self.country:
                filter_id = check_seo_data_exists(None, self.type, self.country, None, None, None, None)
                self.create_filter_feed(filter_id)

            if self.type and self.city:
                filter_id = check_seo_data_exists(None, self.type, self.country, self.city, None, None, None)
                self.create_filter_feed(filter_id)

    def get_absolute_url(self):

        subject = 'u'
        sslug = self.user.user_profile.slug

        if self.company:
            subject = 'c'
            sslug = self.company.slug

        url = '/post/' + subject + '/' + sslug + '/' + self.slug

        url = url + '/' + self.post_language

        return url

    unique_together = ("user", "company", "slug")

    def __unicode__(self):
        return self.id


def update_posts_on_suggested_category_processed(sender, instance, **kwargs):
    if instance.pk and instance.reviewed:
        old_instance = SuggestedCategory.objects.get(pk=instance.pk)
        if not old_instance.reviewed:
            posts = Post.objects.filter(suggested_category=instance.id)
            for post in posts:
                if instance.category:
                    post.category = instance.category
                    post.suggested_category = None
                    post.save()


pre_save.connect(update_posts_on_suggested_category_processed, sender=SuggestedCategory)


def check_seo_data_exists(category, post_type, country,
                          city, seniority,
                          job_function, job_type):
    filter_list = Q()
    if category:
        filter_list = filter_list & Q(category=category)
    else:
        filter_list = filter_list & Q(category__isnull=True)
    if post_type:
        filter_list = filter_list & Q(post_type=post_type)
    else:
        filter_list = filter_list & Q(post_type__isnull=True)
    if country:
        filter_list = filter_list & Q(country=country)
    else:
        filter_list = filter_list & Q(country__isnull=True)
    if city:
        filter_list = filter_list & Q(city=city)
    else:
        filter_list = filter_list & Q(city__isnull=True)
    if seniority:
        filter_list = filter_list & Q(seniority=seniority)
    else:
        filter_list = filter_list & Q(seniority__isnull=True)
    if job_type:
        filter_list = filter_list & Q(job_type=job_type)
    else:
        filter_list = filter_list & Q(job_type__isnull=True)
    if job_function:
        filter_list = filter_list & Q(job_function=job_function)
    else:
        filter_list = filter_list & Q(job_function__isnull=True)

    try:
        obj = PostSEOData.objects.get(filter_list)
    except PostSEOData.DoesNotExist:
        obj = PostSEOData(category=category, post_type=post_type, country=country, city=city, job_function=job_function,
                          seniority=seniority, job_type=job_type)
        obj.save()

    return obj.id


def create_post_objects_after_save(sender, instance, created, **kwargs):
    if created and instance.category:
        obj = PostCategory(post_id=instance.pk, category=instance.category)
        obj.save()
    if created:
        obj = PostEventsQty(post=instance)
        obj.save()
        instance.check_seo_data()
    instance.create_hashtags()


def update_feed_on_post_save(sender, instance, created, **kwargs):
    if created and instance.published:
        instance.create_feed()


def check_post_objects_on_save(sender, instance, **kwargs):
    if instance.pk:

        try:
            old_post = Post.objects.get(pk=instance.pk)
            old_category = old_post.category

        except:
            old_category = None
            old_post = None

        if old_category != instance.category:
            if old_category != None:
                PostCategory.objects.filter(post_id=instance.pk).delete()

            if instance.category:
                object = PostCategory(post_id=instance.pk, category=instance.category)
                object.save()

        if old_post is not None:

            if old_post.published != instance.published:

                if instance.published:
                    qty = 1
                    instance.create_feed()
                else:
                    qty = -1
                instance.update_foreign_instances_qty(qty)

                if instance.type.code == 'review':
                    instance.post_review.update_instances_qty_on_review_saved(qty, instance.post_review.rating)

            if not old_post.allow_index and instance.allow_index and not instance.slug and instance.post_title:
                if instance.company:
                    queryset = Post.objects.filter(company=instance.company)
                else:
                    queryset = Post.objects.filter(user=instance.user)
                unique_slugify(instance, instance.post_title, queryset=queryset)
                if not instance.description:
                    instance.description = truncate_html_description(instance.comment)
                    instance.save()


def update_general_info_on_post_save(sender, instance, created, **kwargs):
    if created:
        if instance.country:
            if not instance.country.posts_exist:
                instance.country.posts_exist = True
                instance.country.save()

        if instance.city:
            if not instance.city.posts_exist:
                instance.city.posts_exist = True
                instance.city.save()


def update_feed_on_post_delete(sender, instance, **kwargs):
    if instance.type:
        if instance.type.code and instance.published:
            delete_activity_by_instance(instance)


def remove_tag_feed(instance, tag_id, item_id):
    feed_name = 'tag' + str(instance.type.feed_id)
    foreign_id = 'taggitem:' + str(item_id)
    delete_activity(feed_name, tag_id, foreign_id)


def create_tag_feed(instance, tag_id, item_id):
    feed_name = 'tag' + str(instance.type.feed_id)
    actor = 'auth.User:' + str(instance.user.id)
    verb = 'tagged'
    feed_object = 'taggit.Tag:' + str(tag_id)
    target = 'post.Post:' + str(instance.id)
    foreign_id = 'taggitem:' + str(item_id)
    time = instance.create_date
    add_feed_activity(feed_name, tag_id, verb, actor, feed_object, target, foreign_id, time)


def update_tag_feed_on_tagitem_save(sender, instance, created, **kwargs):
    ct = ContentType.objects.get(app_label="post", model="post")

    if instance.content_type_id == ct.id:
        post = Post.objects.get(pk=instance.object_id)

        if get_update_user_feed_status(post):
            create_tag_feed(post, instance.tag_id, instance.id)


def update_tag_feed_on_tagitem_delete(sender, instance, **kwargs):
    ct = ContentType.objects.get(app_label="post", model="post")

    if instance.content_type_id == ct.id:
        post = Post.objects.get(pk=instance.object_id)
        if get_update_user_feed_status(post):
            remove_tag_feed(post, instance.tag_id, instance.id)


def update_eventsqty_on_post_save(sender, instance, created, **kwargs):
    if created:
        if instance.shared_post:
            try:
                if instance.shared_post.eventsqty is not None:
                    instance.shared_post.eventsqty.shares = instance.shared_post.eventsqty.shares + 1
                    instance.shared_post.eventsqty.save()
            except PostEventsQty.DoesNotExist:
                object = PostEventsQty(post=instance.shared_post, shares=1)
                object.save()

        if instance.published:
            instance.update_foreign_instances_qty(1)


def update_eventsqty_on_post_delete(sender, instance, **kwargs):
    if instance.shared_post:
        try:
            if instance.shared_post.eventsqty:
                if instance.shared_post.eventsqty.shares > 0:
                    instance.shared_post.eventsqty.shares = instance.shared_post.eventsqty.shares - 1
                    instance.shared_post.eventsqty.save()
        except PostEventsQty.DoesNotExist:
            pass
    if instance.published:
        instance.update_foreign_instances_qty(-1)


post_delete.connect(update_eventsqty_on_post_delete, sender=Post)
pre_delete.connect(update_feed_on_post_delete, sender=Post)

pre_save.connect(check_post_objects_on_save, sender=Post)

post_save.connect(update_general_info_on_post_save, sender=Post)

post_save.connect(create_post_objects_after_save, sender=Post)
post_save.connect(update_eventsqty_on_post_save, sender=Post)
post_save.connect(update_feed_on_post_save, sender=Post)

post_save.connect(update_tag_feed_on_tagitem_save, sender=TaggedItem)
pre_delete.connect(update_tag_feed_on_tagitem_delete, sender=TaggedItem)


class PostCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='post_categories', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def check_seo_data(self):
        if self.category:
            check_seo_data_exists(self.category, None, None, None, None, None, None)

        if self.category and self.post.type:
            filter_id = check_seo_data_exists(self.category, self.post.type, None, None, None, None, None)
            self.post.create_filter_feed(filter_id)

        if self.category and self.post.country:
            check_seo_data_exists(self.category, None, self.post.country, None, None, None, None)

        if self.category and self.post.type and self.post.country:
            filter_id = check_seo_data_exists(self.category, self.post.type, self.post.country, None, None, None, None)
            self.post.create_filter_feed(filter_id)
        if self.category and self.post.city:
            check_seo_data_exists(self.category, None, self.post.country, self.post.city, None, None, None)

        if self.category and self.post.type and self.post.city:
            filter_id = check_seo_data_exists(self.category, self.post.type, self.post.country, self.post.city, None,
                                              None, None)
            self.post.create_filter_feed(filter_id)

    class Meta:
        unique_together = ("post", "category")

    def __unicode__(self):
        return self.id


def update_post_categories_on_save(sender, instance, created, **kwargs):
    if created and instance.category.parent:

        exist = PostCategory.objects.filter(post=instance.post,
                                            category=instance.category.parent).exists()
        if not exist:
            object = PostCategory(post=instance.post, category=instance.category.parent)
            object.save()
    if created:
        instance.category.contents_exist('post')
        instance.check_seo_data()
        # if instance.post.country:
        #     check_category_country(instance.category, instance.post.country)
        # if instance.post.city:
        #     check_category_city(instance.category, instance.post.city)


post_save.connect(update_post_categories_on_save, sender=PostCategory)


def check_post_category_on_delete(sender, instance, **kwargs):
    PostFilterFeed.objects.filter(post=instance.post, post__category=instance.category).delete()


post_delete.connect(check_post_category_on_delete, sender=PostCategory)


class PostRequest(models.Model):
    post = models.OneToOneField(Post, related_name='post_request', primary_key=True)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    price_currency = models.ForeignKey(Currency, null=True, blank=True)
    deadline = models.DateField(null=True, blank=True)
    delivery_address = models.CharField(max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.id


class PostOffering(models.Model):
    OFFERING_TYPES = [
        (1, "1. sales"),
        (2, "2. rent"),
        (3, "2. promotion")
    ]
    post = models.OneToOneField(Post, related_name='post_offering', primary_key=True, on_delete=models.CASCADE)
    type = models.IntegerField(choices=OFFERING_TYPES, default=1)
    unit_type = models.ForeignKey(UnitType, null=True, blank=True, on_delete=models.SET_NULL)
    one_price = models.BooleanField(default=True)
    price_currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.SET_NULL)
    price_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price_usd_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    price_usd = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount = models.IntegerField(null=True, blank=True)
    discount_price_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount_price_usd_from = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    discount_price_usd = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        if self.price:
            self.price_usd = convert_price(self.price, self.price_currency.id, 1)
        if self.price_from:
            self.price_usd_from = convert_price(self.price_from, self.price_currency.id, 1)
        if self.discount_price_from:
            self.discount_price_usd_from = convert_price(self.discount_price_from, self.price_currency.id, 1)
        if self.discount_price:
            self.discount_price_usd = convert_price(self.discount_price, self.price_currency.id, 1)

        return super(PostOffering, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id


class PostRespondStatus(TranslatableModel):
    code = models.CharField(max_length=10, null=True, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )
    position = models.IntegerField(null=True, blank=True)
    icon = models.CharField(max_length=40, null=True, blank=True)
    color_class = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.code


class PostRespond(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='responds', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_responds', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, related_name='company_responds', on_delete=models.SET_NULL, null=True,
                                blank=True)
    status = models.ForeignKey(PostRespondStatus, on_delete=models.SET_NULL, null=True)
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    skype = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default=datetime.now)
    reviewed = models.BooleanField(default=False, blank=None, null=None)
    cover_letter = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=0)
    currency = models.ForeignKey(Currency, null=True, blank=True)
    proposed_price = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)

    @property
    def notification_object_serializer_class(self):
        from .serializers import PostRespondSerializer

        return PostRespondSerializer

    @property
    def activity_object_serializer_class(self):
        from .serializers import PostRespondSerializer

        return PostRespondSerializer

    class Meta:
        unique_together = ("post", "user", "company")

    def __unicode__(self):
        return self.id


def post_owner_notification(sender, instance, created, **kwargs):
    if created:
        create_notification_by_instance(instance)


post_save.connect(post_owner_notification, sender=PostRespond)


class PostRespondDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    respond = models.ForeignKey(PostRespond, related_name='documents', on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.id


class PostRespondChat(models.Model):
    respond = models.OneToOneField(PostRespond, related_name="chat", primary_key=True, on_delete=models.CASCADE)
    chat = models.OneToOneField(Chat, related_name="respond", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("respond", "chat")

    def __unicode__(self):
        return self.id


def create_post_respond_chat(sender, instance, created, **kwargs):
    if created:
        chat_type = 3
        if instance.post.type.code == 'offering':
            chat_type = 4
        if instance.post.type.code == 'request':
            chat_type = 6
        chat = Chat(type=chat_type)
        chat.save()
        respond_chat = PostRespondChat(respond=instance, chat=chat)
        respond_chat.save()

        if instance.company:
            participant = ChatParticipant(chat=chat, company=instance.company)
        else:
            participant = ChatParticipant(chat=chat, user=instance.user)

        participant.save()

        if instance.post.company:
            participant = ChatParticipant(chat=chat, company=instance.post.company)

        else:
            participant = ChatParticipant(chat=chat, user=instance.post.user)
        participant.save()

        cover_letter = ''
        if instance.post.post_title:
            cover_letter = '<h3><b>' + str(instance.post.post_title) + '</b></h3>'
        if instance.cover_letter:
            cover_letter = cover_letter + instance.cover_letter

        create_message(chat.id, 7, instance.user_id, instance.company_id,
                       cover_letter)


post_save.connect(create_post_respond_chat, sender=PostRespond)


def change_post_responds_qty(instance, qty):
    if instance:
        if instance.post.eventsqty is not None:
            instance.post.eventsqty.update_events_qty('responds', qty)
            if instance.reviewed == False:
                instance.post.eventsqty.update_events_qty('new_responds', qty)
        elif qty > 0:
            obj = PostEventsQty(post=instance.post, new_responds=1, responds=1)
            obj.save()
        if instance.status.code == 'new':
            if instance.post.company:
                if instance.post.type.code == 'request':
                    instance.post.company.eventsqty.update_events_qty('new_request_responds', qty)
                if instance.post.type.code == 'offering':
                    instance.post.company.eventsqty.update_events_qty('new_offering_responds', qty)
            else:
                if instance.post.type.code == 'request':
                    instance.post.user.user_profile.eventsqty.update_events_qty('new_request_responds', qty)
                if instance.post.type.code == 'offering':
                    instance.post.user.user_profile.eventsqty.update_events_qty('new_offering_responds', qty)

            if instance.company:
                if instance.post.type.code == 'request':
                    instance.company.eventsqty.update_events_qty('open_request_responds', qty)
                if instance.post.type.code == 'offering':
                    instance.company.eventsqty.update_events_qty('your_open_offering_responds', qty)
            else:
                if instance.post.type.code == 'request':
                    instance.user.user_profile.eventsqty.update_events_qty('open_request_responds', qty)
                if instance.post.type.code == 'offering':
                    instance.user.user_profile.eventsqty.update_events_qty('your_open_offering_responds', qty)


def update_post_responds_qty(sender, instance, created, **kwargs):
    if created and instance.post:
        change_post_responds_qty(instance, 1)


post_save.connect(update_post_responds_qty, sender=PostRespond)


def delete_post_responds_qty(sender, instance, **kwargs):
    change_post_responds_qty(instance, -1)


post_delete.connect(delete_post_responds_qty, sender=PostRespond)


def check_post_responds_qty_on_save(sender, instance, **kwargs):
    if instance.post:

        try:
            old_respond = PostRespond.objects.get(pk=instance.pk)
        except:
            old_respond = None

        if old_respond:
            if old_respond.reviewed != instance.reviewed:
                if instance.reviewed:
                    qty = -1
                else:
                    qty = 1

                instance.post.eventsqty.new_responds = instance.post.eventsqty.new_responds + qty
                instance.post.eventsqty.save()

                if instance.post.company:
                    if instance.post.type.code == 'request':
                        instance.post.company.eventsqty.update_events_qty('new_request_responds', qty)
                    if instance.post.type.code == 'offering':
                        instance.post.company.eventsqty.update_events_qty('new_offering_responds', qty)
                else:
                    if instance.post.type.code == 'request':
                        instance.post.user.user_profile.eventsqty.update_events_qty('new_request_responds', qty)
                    if instance.post.type.code == 'offering':
                        instance.post.user.user_profile.eventsqty.update_events_qty('new_offering_responds', qty)

            if old_respond.status != instance.status:
                if old_respond.status.code == 'new':
                    qty = -1
                else:
                    qty = 1

                if instance.company:
                    if instance.post.type.code == 'request':
                        instance.company.eventsqty.update_events_qty('your_open_request_responds', qty)
                    if instance.post.type.code == 'offering':
                        instance.company.eventsqty.update_events_qty('your_open_offering_responds', qty)
                else:
                    if instance.post.type.code == 'request':
                        instance.user.user_profile.eventsqty.update_events_qty('your_open_request_responds', qty)
                    if instance.post.type.code == 'offering':
                        instance.user.user_profile.eventsqty.update_events_qty('your_open_offering_responds', qty)


pre_save.connect(check_post_responds_qty_on_save, sender=PostRespond)


class PostJob(models.Model):
    post = models.OneToOneField(Post, related_name='post_job', primary_key=True, on_delete=models.CASCADE)
    job_type = models.ForeignKey(JobType, blank=True, null=True, on_delete=models.SET_NULL)
    job_function = models.ForeignKey(JobFunction, blank=True, null=True, on_delete=models.SET_NULL)
    seniority = models.ForeignKey(SeniorityLabel, blank=True, null=True, on_delete=models.SET_NULL)
    resume_required = models.BooleanField(default=False)
    salary_currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.SET_NULL)
    salary = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    salary_usd = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)

    def check_seo_data(self):

        # if self.post.category:
        if self.seniority:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, self.seniority, None, None)
            self.post.create_filter_feed(filter_id)

        if self.job_function:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, None, self.job_function, None)
            self.post.create_filter_feed(filter_id)
        if self.job_type:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, None, None, self.job_type)
            self.post.create_filter_feed(filter_id)
        if self.seniority and self.job_function:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, self.seniority,
                                              self.job_function, None)
            self.post.create_filter_feed(filter_id)
        if self.seniority and self.job_type:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, self.seniority, None,
                                              self.job_type)
            self.post.create_filter_feed(filter_id)
        if self.seniority and self.job_function and self.job_type:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, self.seniority,
                                              self.job_function, self.job_type)
            self.post.create_filter_feed(filter_id)
        if self.job_function and self.job_type:
            filter_id = check_seo_data_exists(None, self.post.type, None, None, None,
                                              self.job_function, self.job_type)
            self.post.create_filter_feed(filter_id)

        if self.post.country:
            if self.seniority:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None,
                                                  self.seniority, None, None)
                self.post.create_filter_feed(filter_id)
            if self.job_function:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None, None,
                                                  self.job_function,
                                                  None)
                self.post.create_filter_feed(filter_id)
            if self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None, None, None,
                                                  self.job_type)
                self.post.create_filter_feed(filter_id)
            if self.seniority and self.job_function:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None, self.seniority,
                                                  self.job_function, None)
                self.post.create_filter_feed(filter_id)
            if self.seniority and self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None, self.seniority, None,
                                                  self.job_type)
                self.post.create_filter_feed(filter_id)
            if self.seniority and self.job_function and self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None, self.seniority,
                                                  self.job_function, self.job_type)
                self.post.create_filter_feed(filter_id)
            if self.job_function and self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, None, None,
                                                  self.job_function, self.job_type)
                self.post.create_filter_feed(filter_id)

        if self.post.city:
            if self.seniority:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city,
                                                  self.seniority, None,
                                                  None)
                self.post.create_filter_feed(filter_id)
            if self.job_function:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city, None,
                                                  self.job_function,
                                                  None)
                self.post.create_filter_feed(filter_id)
            if self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city, None, None,
                                                  self.job_type)
                self.post.create_filter_feed(filter_id)
            if self.seniority and self.job_function:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city,
                                                  self.seniority,
                                                  self.job_function, None)
                self.post.create_filter_feed(filter_id)
            if self.seniority and self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city,
                                                  self.seniority, None,
                                                  self.job_type)
                self.post.create_filter_feed(filter_id)
            if self.seniority and self.job_function and self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city,
                                                  self.seniority,
                                                  self.job_function, self.job_type)
                self.post.create_filter_feed(filter_id)
            if self.job_function and self.job_type:
                filter_id = check_seo_data_exists(None, self.post.type, self.post.country, self.post.city, None,
                                                  self.job_function, self.job_type)
                self.post.create_filter_feed(filter_id)

    def save(self, *args, **kwargs):
        if self.salary:
            self.salary_usd = convert_price(self.salary, self.salary_currency.id, 1)

        return super(PostJob, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.id


def create_post_job_seo_data(sender, instance, created, **kwargs):
    if created:
        instance.check_seo_data()


post_save.connect(create_post_job_seo_data, sender=PostJob)


class ApplicantStatus(TranslatableModel):
    code = models.CharField(max_length=10, null=True, unique=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=40)
    )
    position = models.IntegerField(null=True, blank=True)
    icon = models.CharField(max_length=40, null=True, blank=True)
    color_class = models.CharField(max_length=20, null=True, blank=True)

    def __unicode__(self):
        return self.code


class Applicant(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='applicants', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='jobs', on_delete=models.SET_NULL, null=True)
    status = models.ForeignKey(ApplicantStatus, on_delete=models.SET_NULL, null=True)
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    contact_phone = models.CharField(max_length=15, null=True, blank=True)
    skype = models.CharField(max_length=50, null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    resume = models.ForeignKey(File, blank=True, null=True, on_delete=models.SET_NULL)
    salary_exp = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    reviewed = models.BooleanField(default=False, blank=None, null=None)

    cover_letter = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=0)

    @property
    def notification_object_serializer_class(self):
        from .serializers import ApplicantSerializer

        return ApplicantSerializer

    @property
    def activity_object_serializer_class(self):
        from .serializers import ApplicantSerializer

        return ApplicantSerializer

    class Meta:
        unique_together = ("post", "user")

    def __unicode__(self):
        return self.id


def job_owner_notification(sender, instance, created, **kwargs):
    if created:
        create_notification_by_instance(instance)


post_save.connect(job_owner_notification, sender=Applicant)


class ApplicantChat(models.Model):
    applicant = models.OneToOneField(Applicant, related_name="chat", primary_key=True, on_delete=models.CASCADE)
    chat = models.OneToOneField(Chat, related_name="applicant", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("applicant", "chat")

    def __unicode__(self):
        return self.id


def create_applicant_chat(sender, instance, created, **kwargs):
    if created:

        chat = Chat(type=5)
        chat.save()
        applicant_chat = ApplicantChat(applicant=instance, chat=chat)
        applicant_chat.save()

        participant = ChatParticipant(chat=chat, user=instance.user)
        participant.save()
        if instance.post.company:
            participant = ChatParticipant(chat=chat, company=instance.post.company)
            participant.save()
        else:
            participant = ChatParticipant(chat=chat, user=instance.post.user)
            participant.save()

        cover_letter = ''
        if instance.post.post_title:
            cover_letter = '<h3><b>' + str(instance.post.post_title) + '</b></h3>'
        if instance.cover_letter:
            cover_letter = cover_letter + instance.cover_letter
        create_message(chat.id, 6, instance.user_id, None,
                       cover_letter)


post_save.connect(create_applicant_chat, sender=Applicant)


# def delete_applicant_chat(sender, instance, **kwargs):
#     if instance.chat:
#         instance.chat.delete()
#
# post_delete.connect(delete_applicant_chat, sender=ApplicantChat)

def update_post_applicants_qty(sender, instance, created, **kwargs):
    if created and instance.post:

        if instance.post.eventsqty is not None:
            instance.post.eventsqty.update_events_qty('applicants', 1)
        else:
            obj = PostEventsQty(post=instance.post, new_applicants=1, applicants=1)
            obj.save()

        if instance.post.company:
            instance.post.company.eventsqty.update_events_qty('new_job_responds', 1)
        else:
            instance.post.user.user_profile.eventsqty.update_events_qty('new_job_responds', 1)
        instance.user.user_profile.eventsqty.update_events_qty('your_open_job_responds', 1)


post_save.connect(update_post_applicants_qty, sender=Applicant)


def delete_post_applicants_qty(sender, instance, **kwargs):
    if instance.post:
        instance.post.eventsqty.update_events_qty('applicants', -1)

        if instance.status.code == 'new' or instance.status.code == 'interview':
            instance.user.user_profile.eventsqty.update_events_qty('your_open_job_responds', -1)

        if not instance.reviewed:
            if instance.post.company:
                instance.post.company.eventsqty.update_events_qty('new_job_responds', -1)
            else:
                instance.post.user.user_profile.eventsqty.update_events_qty('new_job_responds', -1)


post_delete.connect(delete_post_applicants_qty, sender=Applicant)


def check_post_applicants_qty_on_save(sender, instance, **kwargs):
    if instance.post:

        try:
            old_applicant = Applicant.objects.get(pk=instance.pk)


        except:
            old_applicant = None

        if old_applicant:
            if old_applicant.reviewed != instance.reviewed:
                if instance.reviewed:
                    qty = -1
                else:
                    qty = 1

                instance.post.eventsqty.new_applicants = instance.post.eventsqty.new_applicants + qty
                instance.post.eventsqty.save()

                if instance.post.company:
                    instance.post.company.eventsqty.update_events_qty('new_job_responds', qty)
                else:
                    instance.post.user.user_profile.eventsqty.update_events_qty('new_job_responds', qty)

            if old_applicant.status != instance.status:
                qty = 0
                if (old_applicant.status.code == 'new' or old_applicant.status.code == 'interview') and (
                        instance.status.code != 'new' and instance.status.code != 'interview'):
                    qty = -1
                if (old_applicant.status.code != 'new' and old_applicant.status.code != 'interview') and (
                        instance.status.code == 'new' or instance.status.code == 'interview'):
                    qty = 1

                instance.user.user_profile.eventsqty.update_events_qty('your_open_job_responds', qty)


pre_save.connect(check_post_applicants_qty_on_save, sender=Applicant)


class PostDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='documents', on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.id


class PostImage(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    file = models.ForeignKey(UserImage, blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        order_with_respect_to = 'post'

    def __unicode__(self):
        return self.id


def delete_post_image_on_delete(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete()


post_delete.connect(delete_post_image_on_delete, sender=PostImage)


class PostRequestPosition(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='post_request_positions', on_delete=models.CASCADE)
    name = models.CharField(max_length=250, null=True, blank=True)
    unit = models.ForeignKey(UnitType, null=True, blank=True, on_delete=models.SET_NULL)
    quantity = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    @property
    def index(self):
        return self.id

    def __unicode__(self):
        return self.id


class PostAttribute(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='attributes', null=True, blank=True, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=40, null=True, blank=True)
    user_attribute = models.BooleanField(default=True)
    multiple = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.id


class PostAttributeValue(models.Model):
    id = models.BigAutoField(primary_key=True)
    post_attribute = models.ForeignKey(PostAttribute, related_name='values')
    value_string = models.CharField(max_length=150, blank=True, null=True)
    value_number = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    value_integer = models.IntegerField(null=True, blank=True)
    value_boolean = models.BooleanField(default=False, blank=True)
    value_list = models.ForeignKey(AttributeValue, blank=True, null=True)

    def __unicode__(self):
        return self.id


class PostReview(models.Model):
    post = models.OneToOneField(Post, related_name='post_review', primary_key=True)

    advantages = models.TextField(blank=True, null=True)
    disadvantages = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(default=0)

    def update_instances_qty_on_review_saved(self, qty, rating):
        if self.post.type.code == 'review':
            if self.post.related_company:
                self.post.related_company.update_rating(qty, rating)
            if self.post.related_user:
                self.post.related_user.user_profile.update_rating(qty, rating)
            if self.post.related_product:
                self.post.related_product.update_rating(qty, rating)

    def __unicode__(self):
        return self.id


def update_review_instances_qty_on_save(sender, instance, created, **kwargs):
    if created and instance.post.published:
        instance.update_instances_qty_on_review_saved(1, instance.rating)


def update_review_instances_qty_on_delete(sender, instance, **kwargs):
    if instance.post.published:
        instance.update_instances_qty_on_review_saved(-1, instance.rating)


def update_review_instances_qty_on_pre_save(sender, instance, **kwargs):
    if instance.post.published:
        try:
            old_review = PostReview.objects.get(pk=instance.pk)
        except PostReview.DoesNotExist:
            old_review = None

        if old_review:
            if old_review.rating != instance.rating:
                instance.update_instances_qty_on_review_saved(-1, old_review.rating)
                instance.update_instances_qty_on_review_saved(1, instance.rating)


post_delete.connect(update_review_instances_qty_on_delete, sender=PostReview)
pre_save.connect(update_review_instances_qty_on_pre_save, sender=PostReview)
post_save.connect(update_review_instances_qty_on_save, sender=PostReview)


class PostOption(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='post_options', null=True, blank=True)
    position = models.IntegerField(default=0, null=False, blank=False)
    name = models.CharField(max_length=280, null=True, blank=True)
    votes = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['position']

    def __unicode__(self):
        return self.id


class PostOptionVote(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='post_votes', null=True, blank=True, on_delete=models.CASCADE)
    option = models.ForeignKey(PostOption, related_name='option_votes', null=True, blank=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user_votes', null=False, blank=False, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post", "option")

    def __unicode__(self):
        return self.id


def update_post_votes_on_save(sender, instance, created, **kwargs):
    if created:
        instance.post.eventsqty.update_events_qty('votes', 1)
        instance.option.votes = instance.option.votes + 1
        instance.option.save()


def update_post_votes_on_delete(sender, instance, **kwargs):
    if instance.post:
        instance.post.eventsqty.update_events_qty('votes', -1)
        try:
            if instance.option:
                instance.option.votes = instance.option.votes - 1
                if instance.option.votes >= 0:
                    instance.option.save()
        except PostOption.DoesNotExist:
            pass


post_save.connect(update_post_votes_on_save, sender=PostOptionVote)
post_delete.connect(update_post_votes_on_delete, sender=PostOptionVote)


class PostEventsQty(UpdateQtyMixin, models.Model):
    post = models.OneToOneField(Post, related_name='eventsqty', primary_key=True, on_delete=models.CASCADE)
    comments = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    applicants = models.PositiveIntegerField(default=0)
    new_applicants = models.PositiveIntegerField(default=0)
    responds = models.PositiveIntegerField(default=0)
    new_responds = models.PositiveIntegerField(default=0)
    votes = models.PositiveIntegerField(default=0)
    impressions = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)
    user_impressions = models.PositiveIntegerField(default=0)
    user_views = models.PositiveIntegerField(default=0)
    engagements = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.id


def get_date():
    date = datetime.now().timestamp()

    return str(date)


class PostUserImpression(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=False, related_name='views', on_delete=models.CASCADE)
    impression = models.BooleanField(default=True)
    view = models.BooleanField(default=False)
    timestamp = models.CharField(null=False, blank=False, default=get_date, max_length=20)
    create_date = models.DateField(auto_now_add=True)
    event_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user", "view", 'impression', "timestamp", "create_date")

    def __unicode__(self):
        return self.id


def change_view_and_impressions_qty(instance, qty):
    if instance.post:
        if instance.user:
            if instance.view:
                instance.post.eventsqty.update_events_qty('user_views', qty)
            if instance.impression:
                instance.post.eventsqty.update_events_qty('user_impressions', qty)
        else:
            if instance.view:
                instance.post.eventsqty.update_events_qty('views', qty)
            if instance.impression:
                instance.post.eventsqty.update_events_qty('impressions', qty)


def update_eventsqty_on_view_save(sender, instance, created, **kwargs):
    if created:
        change_view_and_impressions_qty(instance, 1)


def update_eventsqty_on_view_delete(sender, instance, **kwargs):
    change_view_and_impressions_qty(instance, -1)


post_save.connect(update_eventsqty_on_view_save, sender=PostUserImpression)
post_delete.connect(update_eventsqty_on_view_delete, sender=PostUserImpression)


class PostUserEngagement(models.Model):
    ENGAGEMENTS_TYPES = [
        (1, "1. Link Click"),
        (2, "2. Respond"),
        (3, "3. ProfileClick"),
        (4, "4. AddToFavorite"),
        (5, "5. ShowMore"),
        (6, "6. Vote"),
        (7, "7. ImagePreview"),
        (8, "8. Comments or Like"),
    ]
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='engagements', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, related_name='engagements', on_delete=models.CASCADE)
    timestamp = models.CharField(null=False, blank=False, default=get_date, max_length=20)
    type = models.IntegerField(choices=ENGAGEMENTS_TYPES, default=1)
    create_date = models.DateField(auto_now_add=True)
    event_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user", "timestamp", 'create_date', 'type')

    def __unicode__(self):
        return self.id


def update_eventsqty_on_engagement_save(sender, instance, created, **kwargs):
    if created:
        if instance.post:
            instance.post.eventsqty.update_events_qty('engagements', 1)


def update_eventsqty_engagement_delete(sender, instance, **kwargs):
    if instance.post:
        instance.post.eventsqty.update_events_qty('engagements', -1)


post_save.connect(update_eventsqty_on_engagement_save, sender=PostUserEngagement)
post_delete.connect(update_eventsqty_engagement_delete, sender=PostUserEngagement)


class PostLike(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, related_name='likes', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    @property
    def activity_object_serializer_class(self):
        from .serializers import PostLikeSerializer
        return PostLikeSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import PostLikeSmallSerializer

        return PostLikeSmallSerializer

    class Meta:
        unique_together = ("user", "post")

    def __unicode__(self):
        return self.id


def update_eventsqty_on_post_like_save(sender, instance, created, **kwargs):
    if created:
        if instance.post:
            try:
                if instance.post.eventsqty is not None:
                    instance.post.eventsqty.likes = instance.post.eventsqty.likes + 1
                    instance.post.eventsqty.save()
            except PostEventsQty.DoesNotExist:
                obj = PostEventsQty(post=instance.post, likes=1)
                obj.save()


def update_user_feed_on_like(sender, instance, created, **kwargs):
    if created and instance.user_id != instance.post.user_id:
        create_feed_activity(instance)


def update_user_feed_on_like_delete(sender, instance, **kwargs):
    if instance.user_id != instance.post.user_id:
        delete_activity_by_instance(instance)


def update_eventsqty_on_post_like_delete(sender, instance, **kwargs):
    if instance.post:
        try:
            if instance.post.eventsqty:
                instance.post.eventsqty.likes = instance.post.eventsqty.likes - 1
                instance.post.eventsqty.save()
        except PostEventsQty.DoesNotExist:
            pass


post_save.connect(update_eventsqty_on_post_like_save, sender=PostLike)
post_delete.connect(update_eventsqty_on_post_like_delete, sender=PostLike)
post_save.connect(update_user_feed_on_like, sender=PostLike)
post_delete.connect(update_user_feed_on_like_delete, sender=PostLike)


class PostCommentUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='commentators', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, related_name='comments_on_posts', on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "post")

    def __unicode__(self):
        return self.id


class PostComment(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, related_name='comments', on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='child_comments', null=True, blank=True, default=None,
                               on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    image = models.ForeignKey(UserImage, blank=True, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    @property
    def activity_object_serializer_class(self):
        from .serializers import PostCommentSerializer
        return PostCommentSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import PostCommentSmallSerializer

        return PostCommentSmallSerializer

    def __unicode__(self):
        return "%s| %s" % (self.id, self.text)


def create_comment_objects_after_save(sender, instance, created, **kwargs):
    if created:
        object = PostCommentEventsQty(comment=instance)
        object.save()

    if created and instance.parent == None:
        user_exist = PostCommentUser.objects.filter(post=instance.post, user=instance.user)
        if not user_exist:
            object = PostCommentUser(post=instance.post, user=instance.user)
            object.save()

    if created and instance.parent:
        user_exist = PostParentCommentUser.objects.filter(comment=instance.parent, user=instance.user)
        if not user_exist:
            object = PostParentCommentUser(comment=instance.parent, user=instance.user)
            object.save()


def update_eventsqty_on_comment_save(sender, instance, created, **kwargs):
    if created:
        if instance.parent:
            if instance.parent.eventsqty:
                instance.parent.eventsqty.comments = instance.parent.eventsqty.comments + 1
                instance.parent.eventsqty.save()

            else:
                object = PostCommentEventsQty(comment=instance.parent, comments=1)
                object.save()

        try:
            instance.post.eventsqty.comments = instance.post.eventsqty.comments + 1
            instance.post.eventsqty.save()

        except ObjectDoesNotExist:
            object = PostEventsQty(post=instance.post, comments=1)
            object.save()


def update_eventsqty_on_comment_delete(sender, instance, **kwargs):
    try:
        if instance.parent:
            if instance.parent.eventsqty:
                instance.parent.eventsqty.comments = instance.parent.eventsqty.comments - 1
                instance.parent.eventsqty.save()
    except ObjectDoesNotExist:
        pass

    try:
        if instance.post.eventsqty:
            instance.post.eventsqty.comments = instance.post.eventsqty.comments - 1
            instance.post.eventsqty.save()
    except PostEventsQty.DoesNotExist:
        pass


def update_user_feed_on_comment(sender, instance, created, **kwargs):
    if created:
        create_feed_activity(instance)


def update_user_feed_on_comment_delete(sender, instance, **kwargs):
    if instance.user_id != instance.post.user_id:
        delete_activity_by_instance(instance)


post_save.connect(update_eventsqty_on_comment_save, sender=PostComment)
post_save.connect(create_comment_objects_after_save, sender=PostComment)
post_delete.connect(update_eventsqty_on_comment_delete, sender=PostComment)
post_save.connect(update_user_feed_on_comment, sender=PostComment)
post_delete.connect(update_user_feed_on_comment_delete, sender=PostComment)


class PostCommentUrlPreview(models.Model):
    comment = models.OneToOneField(PostComment, related_name='urlpreview', primary_key=True)
    url = models.URLField(blank=True, null=True, max_length=500)
    image = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=300, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    site_name = models.CharField(blank=True, null=True, max_length=50)

    def __unicode__(self):
        return "%s| %s" % (self.id, self.title)


class PostCommentLike(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.ForeignKey(PostComment)
    user = models.ForeignKey(User, null=False, blank=False)
    create_date = models.DateTimeField(auto_now_add=True)

    @property
    def activity_object_serializer_class(self):
        from .serializers import PostCommentLikeSerializer
        return PostCommentLikeSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import PostCommentLikeSmallSerializer

        return PostCommentLikeSmallSerializer

    class Meta:
        unique_together = ("user", "comment")

    def __unicode__(self):
        return self.id


def update_user_feed_on_comment_like(sender, instance, created, **kwargs):
    if created:
        create_feed_activity(instance)


def update_user_feed_on_comment_like__delete(sender, instance, **kwargs):
    delete_activity_by_instance(instance)


post_save.connect(update_user_feed_on_comment_like, sender=PostCommentLike)
post_delete.connect(update_user_feed_on_comment_like__delete, sender=PostCommentLike)


class PostParentCommentUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    comment = models.ForeignKey(PostComment, related_name='commentators', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "comment")

    def __unicode__(self):
        return self.id


class PostCommentEventsQty(models.Model):
    comment = models.OneToOneField(PostComment, related_name='eventsqty', primary_key=True, on_delete=models.CASCADE)
    likes = models.PositiveIntegerField(default=0)
    comments = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.id


def update_eventsqty_on_comment_like_save(sender, instance, created, **kwargs):
    if created:
        if instance.comment:
            if instance.comment.eventsqty:
                instance.comment.eventsqty.likes = instance.comment.eventsqty.likes + 1
                instance.comment.eventsqty.save()

            else:
                object = PostCommentEventsQty(comment=instance.comment, likes=1)
                object.save()


def update_eventsqty_on_comment_like_delete(sender, instance, **kwargs):
    try:
        if instance.comment:
            if instance.comment.eventsqty:
                instance.comment.eventsqty.likes = instance.comment.eventsqty.likes - 1
                instance.comment.eventsqty.save()
    except ObjectDoesNotExist:
        pass


post_save.connect(update_eventsqty_on_comment_like_save, sender=PostCommentLike)
post_delete.connect(update_eventsqty_on_comment_like_delete, sender=PostCommentLike)


class FavoritePost(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, null=False, blank=False, related_name='favorites_posts', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='favorites', on_delete=models.CASCADE)

    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __unicode__(self):
        return self.id


def update_profile_eventsqty_on_favorite_post_save(sender, instance, created, **kwargs):
    if created:
        instance.user.user_profile.eventsqty.update_events_qty('favorite_posts', 1)


def update_profile_eventsqty_on_favorite_post_delete(sender, instance, **kwargs):
    instance.user.user_profile.eventsqty.update_events_qty('favorite_posts', -1)


post_save.connect(update_profile_eventsqty_on_favorite_post_save, sender=FavoritePost)
post_delete.connect(update_profile_eventsqty_on_favorite_post_delete, sender=FavoritePost)


class PostSEOData(models.Model):
    category = models.ForeignKey(Category, blank=True, null=True, default=None, on_delete=models.CASCADE)
    post_type = models.ForeignKey(PostType, blank=True, null=True, default=None, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, blank=True, null=True, default=None, on_delete=models.CASCADE)
    city = models.ForeignKey(City, blank=True, null=True, default=None, on_delete=models.CASCADE)
    job_type = models.ForeignKey(JobType, blank=True, null=True, default=None, on_delete=models.CASCADE)
    job_function = models.ForeignKey(JobFunction, blank=True, null=True, default=None, on_delete=models.CASCADE)
    seniority = models.ForeignKey(SeniorityLabel, blank=True, null=True, default=None, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def get_absolute_url(self):
        url = '/feed'
        lang = translation.get_language()

        url = url + '/' + lang
        url = url + '?'

        is_attributes = False
        if self.post_type:
            url = url + 'post_type=' + self.post_type.code
            is_attributes = True
        if self.country:
            if is_attributes:
                url = url + '&'
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
        if self.job_type:
            if is_attributes:
                url = url + '&'
            url = url + 'job_type=' + self.job_type.slug
            is_attributes = True
        if self.job_function:
            if is_attributes:
                url = url + '&'
            url = url + 'job_function=' + self.job_function.slug

        return url

    def _get_filter_name(self):
        name = ''
        first_name = False
        if self.post_type:
            name = self.post_type.name
            first_name = True

        if self.country:
            if first_name:
                name = name + ', '
            else:
                first_name = True
            name = name + self.country.name

        if self.city:
            if first_name:
                name = name + ', '
            else:
                first_name = True
            name = name + self.city.name
        if self.category:
            if first_name:
                name = name + ', '
            else:
                first_name = True
            name = name + self.category.name
        if self.job_function:
            if first_name:
                name = name + ', '
            else:
                first_name = True
            name = name + self.job_function.name
        if self.job_type:
            if first_name:
                name = name + ', '
            else:
                first_name = True
            name = name + self.job_type.name
        if self.seniority:
            if first_name:
                name = name + ', '
            name = name + self.seniority.name

        return name

    filter_name = property(_get_filter_name)

    @property
    def activity_object_serializer_class(self):
        from .serializers import PostSEOSerializer

        return PostSEOSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import PostSEOSerializer

        return PostSEOSerializer

    class Meta:
        unique_together = ("category", "post_type", "country", "city", "job_type", "job_function", "seniority")

    def __unicode__(self):
        return self.id


class PostSEODataFollower(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='followed_filters', on_delete=models.CASCADE)
    filter = models.ForeignKey(PostSEOData, related_name='followers', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("filter", "user")

    def __unicode__(self):
        return self.id


def follow_filter_feed(sender, instance, created, **kwargs):
    if instance.filter.post_type:
        target = 'filter' + str(instance.filter.post_type.feed_id) + ':' + str(instance.filter.id)
        source = 'timeline_aggregated' + str(instance.filter.post_type.feed_id) + ':' + str(instance.user.id)
        follows = [
            {'source': 'timeline_aggregated:' + str(instance.user.id), 'target': target},
            {'source': source, 'target': target},

        ]
        stream_client.follow_many(follows, activity_copy_limit=10)


def unfollow_filter_feed(sender, instance, **kwargs):
    if instance.filter.post_type:
        target = 'filter' + str(instance.filter.post_type.feed_id)
        source = 'timeline_aggregated' + str(instance.filter.post_type.feed_id)
        feed = feed_manager.get_feed('timeline_aggregated', instance.user.id)
        feed.unfollow(target, instance.filter.id)
        feed = feed_manager.get_feed(source, instance.user.id)
        feed.unfollow(target, instance.filter.id)


post_save.connect(follow_filter_feed, sender=PostSEODataFollower)
post_delete.connect(unfollow_filter_feed, sender=PostSEODataFollower)


class PostFilterFeed(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='filters', on_delete=models.CASCADE)
    filter = models.ForeignKey(PostSEOData, on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("filter", "post")

    def __unicode__(self):
        return self.id


def create_post_filter_feed(sender, instance, created, **kwargs):
    if created and instance.post.published:
        create_feed_activity(instance)


def delete_post_filter_feed(sender, instance, **kwargs):
    delete_activity_by_instance(instance)


post_save.connect(create_post_filter_feed, sender=PostFilterFeed)
post_delete.connect(delete_post_filter_feed, sender=PostFilterFeed)


class Article(TranslatableModel):
    post = models.OneToOneField(Post, related_name='article', primary_key=True, on_delete=models.CASCADE)
    default_lang = models.ForeignKey(Language, blank=True, null=True, on_delete=models.SET_NULL)

    image = models.ForeignKey(UserImage, related_name='article_image', blank=True, null=True, on_delete=models.SET_NULL)
    image_draft = models.ForeignKey(UserImage, related_name='article_draft_image', blank=True, null=True,
                                    on_delete=models.SET_NULL)
    draft_country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    draft_city = models.ForeignKey(City, blank=True, null=True, on_delete=models.SET_NULL)
    draft_category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.SET_NULL)
    allow_index = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    translations = TranslatedFields(
        link_canonical=models.URLField(null=True, blank=True),
        link_canonical_draft=models.URLField(null=True, blank=True),
        title=models.CharField(max_length=500, blank=True, null=True),
        seo_title=models.CharField(max_length=500, blank=True, null=True),
        description=models.CharField(max_length=500, blank=True, null=True),
        text=models.TextField(blank=True, null=True),
        title_draft=models.CharField(max_length=500, blank=True, null=True),
        seo_title_draft=models.CharField(max_length=500, blank=True, null=True),
        description_draft=models.CharField(max_length=500, blank=True, null=True),
        text_draft=models.TextField(blank=True, null=True)
    )

    to_publish = models.BooleanField(default=True)

    def _get_default_title(self):

        text = self.post.title

        return text

    default_title = property(_get_default_title)

    def get_absolute_url(self):

        subject = 'u'
        sslug = self.post.user.user_profile.slug

        if self.post.company:
            subject = 'c'
            sslug = self.post.company.slug

        url = '/article/' + subject + '/' + sslug + '/' + self.post.slug

        url = url + '/' + self.language_code

        return url

    def delete_translation(self, lang):
        opts = self._meta
        translations_model = opts.translations_model

        obj = translations_model.objects.select_related('master').get(
            master__pk=self.pk,
            language_code=lang)

        obj.delete()

    def prepare_published_fields(self):
        self.title = self.title_draft
        if not self.seo_title_draft:
            self.seo_title_draft = self.title_draft
        if not self.description_draft:
            self.description_draft = truncate_html_description(self.text_draft)

        self.seo_title = self.seo_title_draft
        self.description = self.description_draft
        new_text = self.text_draft.replace('<img loading="lazy"', '<img')
        self.text = new_text.replace('<img', '<img loading="lazy"')
        self.link_canonical = self.link_canonical_draft

        self.save()

    def __unicode__(self):
        return self.id


class RelatedPost(models.Model):
    id = models.BigAutoField(primary_key=True)
    post = models.ForeignKey(Post, related_name='related_posts', on_delete=models.CASCADE)
    related_post = models.ForeignKey(Post, related_name='main_posts', on_delete=models.CASCADE)
    comment = models.CharField(blank=True, null=True, max_length=20)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "related_post")
        ordering = ('id',)

    def __unicode__(self):
        return self.id
