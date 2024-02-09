from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from catalog.company.models import Company
from django.db.models.signals import post_save, post_delete
from datetime import datetime
from django.utils import timezone

from catalog.getstream.utils import create_notification_by_instance


class Chat(models.Model):
    CHAT_TYPES = [
        (1, "1. Contact"),
        (2, "2. Request"),
        (3, "3. Post"),
        (4, "4. Offering"),
        (5, "5. Job"),
        (6, "6. Post request"),
    ]
    id = models.BigAutoField(primary_key=True)
    type = models.IntegerField(choices=CHAT_TYPES, default=1)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default=datetime.now)

    @property
    def activity_object_serializer_class(self):
        from .serializers import ChatSerializer

        return ChatSerializer

    @property
    def notification_object_serializer_class(self):
        from .serializers import ChatSmallSerializer

        return ChatSmallSerializer

    def __unicode__(self):
        return self.id


def set_user_contact_chat(user_id, contact_id):
    try:
        chat = Chat.objects.filter(type=1, chat_users__user=contact_id)
        chat = chat.get(type=1, chat_users__user=user_id)
    except:
        chat = Chat(type=1)
        chat.save()
        participant = ChatParticipant(chat=chat, user_id=user_id)
        participant.save()
        participant = ChatParticipant(chat=chat, user_id=contact_id)
        participant.save()
    return chat.id


def set_user_with_company_chat(user_id, company_id):
    try:
        chat = Chat.objects.filter(type=1, chat_users__user=user_id)
        chat = chat.get(type=1, chat_users__company=company_id)
    except:
        chat = Chat(type=1)
        chat.save()
        participant = ChatParticipant(chat=chat, company_id=company_id)
        participant.save()
        participant = ChatParticipant(chat=chat, user_id=user_id)
        participant.save()

    return chat.id


class ChatParticipant(models.Model):
    id = models.BigAutoField(primary_key=True)
    chat = models.ForeignKey(Chat, related_name='chat_users')
    user = models.ForeignKey(User, related_name='user_chats', blank=True, null=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, related_name='company_chats', blank=True, null=True, on_delete=models.SET_NULL)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    unread_messages = models.IntegerField(default=0)
    customer = models.BooleanField(default=False, blank=True)
    supplier = models.BooleanField(default=False, blank=True)

    class Meta:
        unique_together = ("chat", "user", "company")

    def __unicode__(self):
        return "%s  %s  %s" % (self.id, self.user, self.company)


class Message(models.Model):
    MESSAGE_TYPES = [
        (1, "1. Message"),
        (2, "2. Contact invitation"),
        (3, "3. Contact accepted"),
        (4, "4. Community invitation"),
        (5, "5. New Request"),
        (6, "6. Job Response"),
        (7, "7. Post Response"),
    ]
    id = models.BigAutoField(primary_key=True)
    chat = models.ForeignKey(Chat)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, blank=True, null=True)
    type = models.IntegerField(choices=MESSAGE_TYPES, default=1)
    message = models.TextField(null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(default=timezone.now)

    @property
    def notification_object_serializer_class(self):
        from .serializers import MessageSerializer

        return MessageSerializer

    @property
    def activity_object_serializer_class(self):
        from .serializers import MessageSerializer

        return MessageSerializer

    def __unicode__(self):
        return "%s  %s  %s  %s" % (self.id, self.chat, self.user, self.update_date)


def create_message(chat, type, user, company, message=''):
    obj = Message(chat_id=chat, type=type, user_id=user, company_id=company, message=message)
    obj.save()

    return obj.id


def notification_participants(sender, instance, created, **kwargs):
    if created and (instance.type == 1):
        create_notification_by_instance(instance)
        obj = Chat.objects.get(pk=instance.chat_id)
        obj.update_date = timezone.now()
        obj.save()


post_save.connect(notification_participants, sender=Message)

# def delete_participants_notificatons (sender, instance, **kwargs):
#     if instance.type == 1 or instance.type == 5:
#         delete_notification(instance)
#
# post_delete.connect(delete_participants_notificatons, sender=Message)
