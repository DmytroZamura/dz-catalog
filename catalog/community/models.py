from __future__ import unicode_literals

from django.db import models
from hvad.models import TranslatableModel, TranslatedFields

from django.contrib.auth.models import User
from catalog.general.models import Country, City
from catalog.file.models import UserImage
from catalog.company.models import Company
from catalog.category.models import Category
from django.db.models.signals import post_delete, post_save, pre_save
from taggit.managers import TaggableManager
from django.core.exceptions import ObjectDoesNotExist
from catalog.getstream.utils import create_notification_by_instance, follow_target_feed, unfollow_target_feed
from hvad.utils import get_translation
from django.conf import settings
from catalog.utils.model_mixins import UpdateQtyMixin


class Community(TranslatableModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(UserImage, blank=True, null=True, on_delete=models.SET_NULL)
    open = models.BooleanField(default=True)
    show_products = models.BooleanField(default=False)
    moderator_check_invite = models.BooleanField(default=False)
    local_community = models.BooleanField(default=False)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    tags = TaggableManager(blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True, db_index=True)
    deleted = models.BooleanField(default=False, blank=True)
    translations = TranslatedFields(
        name=models.CharField(max_length=300),
        description=models.TextField(null=True, blank=True),
        rules=models.TextField(null=True, blank=True)
    )

    def get_email_dict(self, lang):
        try:
            trans = get_translation(self, lang)
        except ObjectDoesNotExist:
            trans = get_translation(self, 'en')
        name = trans.name
        rules = trans.rules
        url = settings.FRONTEND_URL + 'community/' + str(self.id)
        if self.image:
            image = self.image.file.url
        else:
            image = settings.FRONTEND_URL + 'static/assets/img/community.png'
        res = dict()
        res['name'] = name
        res['rules'] = rules
        res['url'] = url
        res['image'] = image
        return res

    def smart_delete(self):
        community = self
        community.deleted = True
        community.image = None
        community.slug = 'community-deleted' + str(community.id)
        community.save()
        community_categories = community.categories
        community_categories.all().delete()
        invitations = community.invitations
        invitations.all().delete()

        try:
            posts = community.community_posts
            for post in posts.all():
                post.smart_delete()

        except ObjectDoesNotExist:
            pass

        members = community.members
        members.all().delete()
        companies = community.companies
        companies.all().delete()

    def _get_name_all_languages(self):
        translations = Community.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.name)
        return values

    def _get_description_all_languages(self):
        translations = Community.objects.language('all').filter(pk=self.pk)
        values = []
        for translation in translations:
            values.append(translation.description)
        return values

    name_all_languages = property(_get_name_all_languages)
    description_all_languages = property(_get_description_all_languages)

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
    def activity_object_serializer_class(self):
        from .serializers import CommunityShortSerializer
        return CommunityShortSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import CommunityShortSerializer
        return CommunityShortSerializer

    def __unicode__(self):
        return self.id


def update_general_info_on_community_save(sender, instance, created, **kwargs):
    if created:
        obj = CommunityEventsQty(community=instance)
        obj.save()

    if instance.country:
        if not instance.country.communities_exist:
            instance.country.communities_exist = True
            instance.country.save()

    if instance.city:
        if not instance.city.communities_exist:
            instance.city.communities_exist = True
            instance.city.save()




post_save.connect(update_general_info_on_community_save, sender=Community)


def delete_community_image_on_save(sender, instance, **kwargs):
    if instance.pk:
        old_instance = Community.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image != instance.image:
            old_instance.image.delete()


pre_save.connect(delete_community_image_on_save, Community)


def delete_community_image_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete()


post_delete.connect(delete_community_image_on_delete, sender=Community)


class CommunityEventsQty(UpdateQtyMixin, models.Model):
    community = models.OneToOneField(Community, related_name='eventsqty', primary_key=True, on_delete=models.CASCADE)
    members = models.PositiveIntegerField(default=0, db_index=True)
    companies = models.PositiveIntegerField(default=0)
    jobposts = models.PositiveIntegerField(default=0)
    publications = models.PositiveIntegerField(default=0)
    offerings = models.PositiveIntegerField(default=0)
    requests = models.PositiveIntegerField(default=0)
    invitations = models.PositiveIntegerField(default=0)
    questions = models.PositiveIntegerField(default=0)
    reviews = models.PositiveIntegerField(default=0)

    def __unicode__(self):
        return self.id


class CommunityMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='communities')
    community = models.ForeignKey(Community, related_name='members')
    admin = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    @property
    def notification_object_serializer_class(self):
        from .serializers import CommunityMemberSerializer
        return CommunityMemberSerializer

    @property
    def activity_object_serializer_class(self):
        from .serializers import CommunityMemberSerializer
        return CommunityMemberSerializer

    class Meta:
        unique_together = ("user", "community")

    def __unicode__(self):
        return self.id


def community_member_notification(sender, instance, created, **kwargs):
    if created and not instance.community.open and not instance.admin:
        create_notification_by_instance(instance, 'user_community_member')


post_save.connect(community_member_notification, sender=CommunityMember)


def notification_on_admin_changed(sender, instance, **kwargs):
    if instance.pk:
        old_instance = CommunityMember.objects.get(pk=instance.pk)
        if old_instance.admin != instance.admin:
            if instance.admin:
                create_notification_by_instance(instance, 'administrator_created')
            else:
                create_notification_by_instance(instance, 'administrator_deleted')


pre_save.connect(notification_on_admin_changed, CommunityMember)


def update_community_data_on_member_save(sender, instance, created, **kwargs):
    if created:
        instance.community.eventsqty.update_events_qty('members', 1)
        instance.user.user_profile.eventsqty.update_events_qty('favorite_communities', 1)


def update_community_data_on_member_delete(sender, instance, **kwargs):
    instance.community.eventsqty.update_events_qty('members', -1)
    instance.user.user_profile.eventsqty.update_events_qty('favorite_communities', -1)


def follow_community_feed(sender, instance, created, **kwargs):
    follow_target_feed('community', instance.user.id, instance.community.id)


def unfollow_community_feed(sender, instance, **kwargs):
    unfollow_target_feed('community',instance.user.id, instance.community.id)



post_save.connect(follow_community_feed, sender=CommunityMember)
post_delete.connect(unfollow_community_feed, sender=CommunityMember)
post_save.connect(update_community_data_on_member_save, sender=CommunityMember)
post_delete.connect(update_community_data_on_member_delete, sender=CommunityMember)


class CommunityCompany(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, related_name='communities', on_delete=models.CASCADE)
    community = models.ForeignKey(Community, related_name='companies', on_delete=models.CASCADE)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("company", "community")

    def __unicode__(self):
        return self.id


def community_company_notification(sender, instance, created, **kwargs):
    if created and not instance.community.open:
        create_notification_by_instance(instance)


post_save.connect(community_company_notification, sender=CommunityCompany)


def update_community_data_on_company_save(sender, instance, created, **kwargs):
    if created:
        instance.community.eventsqty.update_events_qty('companies', 1)


def update_community_data_on_company_delete(sender, instance, **kwargs):
    instance.community.eventsqty.update_events_qty('companies', -1)


post_save.connect(update_community_data_on_company_save, sender=CommunityCompany)
post_delete.connect(update_community_data_on_company_delete, sender=CommunityCompany)


class CommunityInvitation(models.Model):
    id = models.BigAutoField(primary_key=True)
    company = models.ForeignKey(Company, null=True, blank=True, related_name='invitations', on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, related_name='invitations', on_delete=models.CASCADE)
    community = models.ForeignKey(Community, related_name='invitations', on_delete=models.CASCADE)
    message = models.TextField(null=True, blank=True)
    user_acceptance = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    accepted_by_user = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    @property
    def notification_object_serializer_class(self):
        from .serializers import CommunityInvitationSerializer
        return CommunityInvitationSerializer

    @property
    def activity_object_serializer_class(self):
        from .serializers import CommunityInvitationSerializer
        return CommunityInvitationSerializer


    class Meta:
        unique_together = ("company", "community", "user")

    def __unicode__(self):
        return self.id


def community_admin_notification(sender, instance, created, **kwargs):
    if created:
        create_notification_by_instance(instance)


post_save.connect(community_admin_notification, sender=CommunityInvitation)


def update_community_members_on_invitation_save(sender, instance, created, **kwargs):
    if instance.accepted and instance.accepted_by_user:
        if instance.company != None:
            exist = CommunityCompany.objects.filter(community=instance.community,
                                                    company=instance.company).exists()
            if not exist:
                object = CommunityCompany(community=instance.community, company=instance.company)
                object.save()
                CommunityInvitation.objects.get(pk=instance.pk).delete()

        if instance.user != None and instance.company == None:
            exist = CommunityMember.objects.filter(community=instance.community,
                                                   user=instance.user).exists()
            if not exist:
                object = CommunityMember(community=instance.community, user=instance.user)
                object.save()
                CommunityInvitation.objects.get(pk=instance.pk).delete()


post_save.connect(update_community_members_on_invitation_save, sender=CommunityInvitation)


def update_community_eventsqty_on_invitation_save(sender, instance, created, **kwargs):
    if created and not instance.user_acceptance:
        instance.community.eventsqty.update_events_qty('invitations', 1)


def update_community_eventsqty_on_invitation_delete(sender, instance, **kwargs):
    if not instance.user_acceptance:
        instance.community.eventsqty.update_events_qty('invitations', -1)


post_save.connect(update_community_eventsqty_on_invitation_save, sender=CommunityInvitation)
post_delete.connect(update_community_eventsqty_on_invitation_delete, sender=CommunityInvitation)


class CommunityCategory(models.Model):
    id = models.BigAutoField(primary_key=True)
    community = models.ForeignKey(Community, related_name='categories', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    child_qty = models.IntegerField(default=0)
    community_category = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("community", "category")

    def __unicode__(self):
        return "%s  %s  %s" % (self.id, self.community, self.category)


def update_community_categories_on_delete(sender, instance, **kwargs):
    if instance.category.parent:

        try:
            object = CommunityCategory.objects.get(community=instance.community, category=instance.category.parent)

            qty = CommunityCategory.objects.filter(community=instance.community,
                                                   category__parent=object.category).count()
            if qty:
                object.child_qty = qty
            else:
                object.child_qty = 0
            object.save()

            if not object.profile_category:
                childs_exist = CommunityCategory.objects.filter(community=instance.community,
                                                                category__parent=instance.category.parent).exists()
                if not childs_exist:
                    CommunityCategory.objects.filter(community=instance.community,
                                                     category=instance.category.parent).delete()
        except:
            object = None

    childs_exist = CommunityCategory.objects.filter(community=instance.community,
                                                    category__parent=instance.category).exists()
    if childs_exist:
        object = CommunityCategory(community=instance.community, category=instance.category)
        object.save()


def update_community_categories_on_save(sender, instance, created, **kwargs):
    if created and instance.category.parent:

        exist = CommunityCategory.objects.filter(community=instance.community,
                                                 category=instance.category.parent).exists()
        if not exist:
            object = CommunityCategory(community=instance.community, category=instance.category.parent, child_qty=1)
            object.save()
        else:
            parent = CommunityCategory.objects.get(community=instance.community,
                                                   category=instance.category.parent)
            qty = CommunityCategory.objects.filter(community=instance.community,
                                                   category__parent=parent.category).count()
            if qty:
                parent.child_qty = qty
            else:
                parent.child_qty = 0
            parent.save()
    if created:
        instance.category.contents_exist('community')
        # if instance.community.country:
        #     check_category_country(instance.category, instance.community.country)
        #
        # if instance.community.city:
        #     check_category_city(instance.category, instance.community.city)


post_save.connect(update_community_categories_on_save, sender=CommunityCategory)
post_delete.connect(update_community_categories_on_delete, sender=CommunityCategory)
