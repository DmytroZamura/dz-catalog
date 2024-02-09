from __future__ import absolute_import
from django.contrib import admin

from .models import TagQty, TagFollower



class TagQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TagQty._meta.fields]

    class Meta:
        model = TagQty


admin.site.register(TagQty, TagQtyAdmin)


class TagFollowerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in TagFollower._meta.fields]

    class Meta:
        model = TagFollower


admin.site.register(TagFollower, TagFollowerAdmin)