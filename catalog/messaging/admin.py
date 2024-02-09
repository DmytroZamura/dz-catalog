from __future__ import absolute_import
from django.contrib import admin
from .models import Chat, ChatParticipant, Message


class ChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Chat._meta.fields]

    class Meta:
        model = Chat

admin.site.register(Chat, ChatAdmin)

class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ChatParticipant._meta.fields]

    class Meta:
        model = ChatParticipant

admin.site.register(ChatParticipant, ChatParticipantAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Message._meta.fields]

    class Meta:
        model = Message

admin.site.register(Message, MessageAdmin)

