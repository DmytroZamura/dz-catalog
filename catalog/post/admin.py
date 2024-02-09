from __future__ import absolute_import
from django.contrib import admin
from .models import Post, PostCategory, PostType, PostRequest, PostDocument, PostRequestPosition, PostImage, \
    PostAttribute, PostAttributeValue, PostOffering, PostComment, PostCommentEventsQty, PostCommentLike, \
    PostCommentUrlPreview, PostEventsQty, PostLike, PostJob, Applicant, ApplicantChat, ApplicantStatus, PostRespond, \
    PostRespondChat, PostRespondDocument, PostRespondStatus, FavoritePost, PostReview, PostOption, PostOptionVote, \
    PostSEOData, Article, PostSEODataFollower, PostFilterFeed, PostUserImpression, PostUserEngagement, RelatedPost

from hvad.admin import TranslatableAdmin


class PostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Post._meta.fields]
    raw_id_fields = ('country', 'city', 'category',)
    search_fields = ['slug', 'pk']

    class Meta:
        model = Post


admin.site.register(Post, PostAdmin)


class RelatedPostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in RelatedPost._meta.fields]
    raw_id_fields = ('post', 'related_post',)
    search_fields = ['comment']

    class Meta:
        model = RelatedPost


admin.site.register(RelatedPost, RelatedPostAdmin)


class FavoritePostAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FavoritePost._meta.fields]

    class Meta:
        model = FavoritePost


admin.site.register(FavoritePost, FavoritePostAdmin)


class PostSEODataAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostSEOData._meta.fields]
    raw_id_fields = ('country', 'city', 'category', 'post_type', 'job_type', 'job_function', 'seniority',)

    class Meta:
        model = PostSEOData


admin.site.register(PostSEOData, PostSEODataAdmin)


class PostSEODataFollowerAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostSEODataFollower._meta.fields]

    class Meta:
        model = PostSEODataFollower


admin.site.register(PostSEODataFollower, PostSEODataFollowerAdmin)


class PostFilterFeedAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostFilterFeed._meta.fields]

    class Meta:
        model = PostFilterFeed


admin.site.register(PostFilterFeed, PostFilterFeedAdmin)


class PostUserImpressionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostUserImpression._meta.fields]

    class Meta:
        model = PostUserImpression


admin.site.register(PostUserImpression, PostUserImpressionAdmin)


class PostUserEngagementAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostUserEngagement._meta.fields]

    class Meta:
        model = PostUserEngagement


admin.site.register(PostUserEngagement, PostUserEngagementAdmin)


class PostCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCategory._meta.fields]

    class Meta:
        model = PostCategory


admin.site.register(PostCategory, PostCategoryAdmin)


class PostTypeAdmin(TranslatableAdmin):
    list_display = [field.name for field in PostType._meta.fields]

    class Meta:
        model = PostType


admin.site.register(PostType, PostTypeAdmin)


class ArticleAdmin(TranslatableAdmin):
    # list_display = [field.name for field in Article._meta.fields]

    list_display = ['default_title', 'to_publish', 'allow_index']

    class Meta:
        model = Article


admin.site.register(Article, ArticleAdmin)


class PostRequestAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostRequest._meta.fields]

    class Meta:
        model = PostRequest


admin.site.register(PostRequest, PostRequestAdmin)


class PostOfferingAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostOffering._meta.fields]

    class Meta:
        model = PostOffering


admin.site.register(PostOffering, PostOfferingAdmin)


class PostJobAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostJob._meta.fields]

    class Meta:
        model = PostJob


admin.site.register(PostJob, PostJobAdmin)


class PostRespondStatusAdmin(TranslatableAdmin):
    list_display = [field.name for field in PostRespondStatus._meta.fields]

    class Meta:
        model = PostRespondStatus


admin.site.register(PostRespondStatus, PostRespondStatusAdmin)


class PostRespondAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostRespond._meta.fields]

    class Meta:
        model = PostRespond


admin.site.register(PostRespond, PostRespondAdmin)


class PostRespondDocumentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostRespondDocument._meta.fields]

    class Meta:
        model = PostRespondDocument


admin.site.register(PostRespondDocument, PostRespondDocumentAdmin)


class PostRespondChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostRespondChat._meta.fields]

    class Meta:
        model = PostRespondChat


admin.site.register(PostRespondChat, PostRespondChatAdmin)


class ApplicantStatusAdmin(TranslatableAdmin):
    list_display = [field.name for field in ApplicantStatus._meta.fields]

    class Meta:
        model = ApplicantStatus


admin.site.register(ApplicantStatus, ApplicantStatusAdmin)


class ApplicantAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Applicant._meta.fields]

    class Meta:
        model = Applicant


admin.site.register(Applicant, ApplicantAdmin)


class ApplicantChatAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ApplicantChat._meta.fields]

    class Meta:
        model = ApplicantChat


admin.site.register(ApplicantChat, ApplicantChatAdmin)


class PostDocumentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostDocument._meta.fields]

    class Meta:
        model = PostDocument


admin.site.register(PostDocument, PostDocumentAdmin)


class PostImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostImage._meta.fields]

    class Meta:
        model = PostImage


admin.site.register(PostImage, PostImageAdmin)


class PostRequestPositionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostRequestPosition._meta.fields]

    class Meta:
        model = PostRequestPosition


admin.site.register(PostRequestPosition, PostRequestPositionAdmin)


class PostAttributeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostAttribute._meta.fields]

    class Meta:
        model = PostAttribute


admin.site.register(PostAttribute, PostAttributeAdmin)


class PostAttributeValueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostAttributeValue._meta.fields]

    class Meta:
        model = PostAttributeValue


admin.site.register(PostAttributeValue, PostAttributeValueAdmin)


class PostCommentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostComment._meta.fields]

    class Meta:
        model = PostComment


admin.site.register(PostComment, PostCommentAdmin)


class PostEventsQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostEventsQty._meta.fields]

    class Meta:
        model = PostEventsQty


admin.site.register(PostEventsQty, PostEventsQtyAdmin)


class PostCommentUrlPreviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCommentUrlPreview._meta.fields]

    class Meta:
        model = PostCommentUrlPreview


admin.site.register(PostCommentUrlPreview, PostCommentUrlPreviewAdmin)


class PostCommentLikeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCommentLike._meta.fields]

    class Meta:
        model = PostCommentLike


admin.site.register(PostCommentLike, PostCommentLikeAdmin)


class PostCommentEventsQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostCommentEventsQty._meta.fields]

    class Meta:
        model = PostCommentEventsQty


admin.site.register(PostCommentEventsQty, PostCommentEventsQtyAdmin)


class PostLikeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostLike._meta.fields]

    class Meta:
        model = PostLike


admin.site.register(PostLike, PostLikeAdmin)


class PostReviewAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostReview._meta.fields]

    class Meta:
        model = PostReview


admin.site.register(PostReview, PostReviewAdmin)


class PostOptionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostOption._meta.fields]

    class Meta:
        model = PostOption


admin.site.register(PostOption, PostOptionAdmin)


class PostOptionVoteAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PostOptionVote._meta.fields]

    class Meta:
        model = PostOptionVote


admin.site.register(PostOptionVote, PostOptionVoteAdmin)
