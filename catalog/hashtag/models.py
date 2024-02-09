from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from taggit.models import Tag
from django.db.models.signals import post_save, post_delete
from django.utils import translation
from catalog.getstream.utils import follow_target_feed, unfollow_target_feed
from catalog.utils.model_mixins import UpdateQtyMixin


class TagFollower(models.Model):
    id = models.BigAutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("tag", "user")

    def __unicode__(self):
        return self.id


class TagQty(UpdateQtyMixin, models.Model):
    tag = models.OneToOneField(Tag, related_name='qty', primary_key=True, on_delete=models.CASCADE)
    followers = models.PositiveIntegerField(default=0, db_index=True)

    def get_absolute_url(self):
        url = '/hashtag/' + self.tag.name
        lang = translation.get_language()
        url = url + '/' + lang
        return url

    def __unicode__(self):
        return self.id


def create_tag_qty(sender, instance, created, **kwargs):
    if created:
        object = TagQty(tag=instance, followers=0)
        object.save()


post_save.connect(create_tag_qty, sender=Tag)


def update_qty_on_follower_save(sender, instance, created, **kwargs):
    instance.user.user_profile.eventsqty.update_events_qty('favorite_tags', 1)
    if created:
        if instance.tag:
            instance.tag.qty.update_events_qty('followers', 1)


def update_qty_on_follower_delete(sender, instance, **kwargs):
    instance.user.user_profile.eventsqty.update_events_qty('favorite_tags', -1)
    if instance.tag:
        instance.tag.qty.update_events_qty('followers', -1)


post_delete.connect(update_qty_on_follower_delete, sender=TagFollower)
post_save.connect(update_qty_on_follower_save, sender=TagFollower)


def follow_tag_feed(sender, instance, created, **kwargs):
    follow_target_feed('tag', instance.user.id, instance.tag.id)


def unfollow_tag_feed(sender, instance, **kwargs):
    unfollow_target_feed('tag', instance.user.id, instance.tag.id)


post_save.connect(follow_tag_feed, sender=TagFollower)
post_delete.connect(unfollow_tag_feed, sender=TagFollower)
