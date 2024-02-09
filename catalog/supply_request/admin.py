from __future__ import absolute_import
from django.contrib import admin
from hvad.admin import TranslatableAdmin
from .models import SupplyRequest, SupplyRequestDocument, SupplyRequestNote, SupplyRequestPosition, SupplyRequestChat, \
    SupplyRequestStatus


class SupplyRequestStatusAdmin(TranslatableAdmin):
    list_display = [field.name for field in SupplyRequestStatus._meta.fields]

    class Meta:
        model = SupplyRequestStatus


admin.site.register(SupplyRequestStatus, SupplyRequestStatusAdmin)


class SupplyRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SupplyRequest._meta.fields]

    class Meta:
        model = SupplyRequest


admin.site.register(SupplyRequest, SupplyRequestAdmin)


class SupplyRequestChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SupplyRequestChat._meta.fields]

    class Meta:
        model = SupplyRequestChat


admin.site.register(SupplyRequestChat, SupplyRequestChatAdmin)


class SupplyRequestDocumentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SupplyRequestDocument._meta.fields]

    class Meta:
        model = SupplyRequestDocument


admin.site.register(SupplyRequestDocument, SupplyRequestDocumentAdmin)


class SupplyRequestNoteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SupplyRequestNote._meta.fields]

    class Meta:
        model = SupplyRequestNote


admin.site.register(SupplyRequestNote, SupplyRequestNoteAdmin)


class SupplyRequestPositionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in SupplyRequestPosition._meta.fields]

    class Meta:
        model = SupplyRequestPosition


admin.site.register(SupplyRequestPosition, SupplyRequestPositionAdmin)
