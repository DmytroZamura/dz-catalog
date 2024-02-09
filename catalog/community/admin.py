from __future__ import unicode_literals
from __future__ import absolute_import
from django.contrib import admin
from hvad.admin import TranslatableAdmin
from .models import Community, CommunityCategory, CommunityCompany, CommunityInvitation, CommunityMember, CommunityEventsQty

class CommunityAdmin(TranslatableAdmin):
    list_display = ['id']

    class Meta:
        model = Community

admin.site.register(Community, CommunityAdmin)


class CommunityEventsQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CommunityEventsQty._meta.fields]
    class Meta:
        model = CommunityEventsQty

admin.site.register(CommunityEventsQty, CommunityEventsQtyAdmin)

class CommunityCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CommunityCategory._meta.fields]

    class Meta:
        model = CommunityCategory

admin.site.register(CommunityCategory, CommunityCategoryAdmin)


class CommunityCompanyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CommunityCompany._meta.fields]

    class Meta:
        model = CommunityCompany

admin.site.register(CommunityCompany, CommunityCompanyAdmin)

class CommunityInvitationAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CommunityInvitation._meta.fields]

    class Meta:
        model = CommunityInvitation

admin.site.register(CommunityInvitation, CommunityInvitationAdmin)

class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = [field.name for field in CommunityMember._meta.fields]

    class Meta:
        model = CommunityMember

admin.site.register(CommunityMember, CommunityMemberAdmin)
