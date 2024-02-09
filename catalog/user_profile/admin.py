from __future__ import absolute_import
from django.contrib import admin
from .models import *
from hvad.admin import TranslatableAdmin


class UserProfileAdmin(TranslatableAdmin):
    list_display = ['id', 'nickname', 'email']
    raw_id_fields = ('country', 'city',)
    search_fields = ['slug', 'nickname', 'email']

    class Meta:
        model = UserProfile

admin.site.register(UserProfile, UserProfileAdmin)


class UserProfileEventsQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserProfileEventsQty._meta.fields]

    class Meta:
        model = UserProfileEventsQty

admin.site.register(UserProfileEventsQty, UserProfileEventsQtyAdmin)


class UserProfileCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserProfileCategory._meta.fields]

    class Meta:
        model = UserProfileCategory

admin.site.register(UserProfileCategory, UserProfileCategoryAdmin)


class UserProfileCountryInterestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserProfileCountryInterest._meta.fields]

    class Meta:
        model = UserProfileCountryInterest

admin.site.register(UserProfileCountryInterest, UserProfileCountryInterestAdmin)




class UserProfileFollowerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserProfileFollower._meta.fields]

    class Meta:
        model = UserProfileFollower

admin.site.register(UserProfileFollower, UserProfileFollowerAdmin)


class ResumeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Resume._meta.fields]

    class Meta:
        model = Resume

admin.site.register(Resume, ResumeAdmin)


class UserActionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in UserAction._meta.fields]

    class Meta:
        model = UserAction

admin.site.register(UserAction, UserActionAdmin)