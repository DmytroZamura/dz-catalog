from django.conf.urls import url
from catalog.hashtag import views

urlpatterns = [
    url(r'^follow-tag/', views.FollowTagView.as_view()),
    url(r'^unfollow-tag/(?P<tag>.+)/$', views.UnfollowTagView.as_view()),
    url(r'^tag-by-slug/(?P<slug>.+)/$', views.TagBySlugView.as_view()),
    url(r'^search-tag-by-name/(?P<name>.+)/$', views.SearchTagsByNameView.as_view()),
    url(r'^favorites-tags-by-page/(?P<page>[0-9]+)/$', views.FavoriteTagsByPageView.as_view()),
    url(r'^tags-by-page/(?P<page>[0-9]+)/$', views.TagsByPageViewView.as_view()),
]
