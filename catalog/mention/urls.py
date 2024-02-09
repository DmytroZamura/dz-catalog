from django.conf.urls import url
from catalog.mention import views

urlpatterns = [

    url(r'^get-mention-by-slug/(?P<slug>.+)/$', views.MentionView.as_view()),
    url(r'^search-mentions-by-name/(?P<name>.+)/$', views.SearchMentionsByName.as_view()),

]
