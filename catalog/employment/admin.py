from __future__ import absolute_import
from django.contrib import admin
from .models import *
from hvad.admin import TranslatableAdmin

class UserProfileEmploymentAdmin (TranslatableAdmin):
    list_display = ['id', 'company_name']

    class Meta:
        model = UserProfileEmployment

admin.site.register(UserProfileEmployment, UserProfileEmploymentAdmin)