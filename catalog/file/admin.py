from __future__ import absolute_import
from django.contrib import admin
from .models import *

from sorl.thumbnail.admin import AdminImageMixin

class FileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in File._meta.fields]

    class Meta:
        model = File

admin.site.register(File, FileAdmin)


class UserImageAdmin(AdminImageMixin, admin.ModelAdmin):
    list_display = [field.name for field in UserImage._meta.fields]

    class Meta:
        model = UserImage

admin.site.register(UserImage, UserImageAdmin)


class UrlImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UrlImage._meta.fields]

    class Meta:
        model = UrlImage

admin.site.register(UrlImage, UrlImageAdmin)