from django.conf.urls import url
from catalog.getstream import views

urlpatterns = [
    url(r'^get-user-token/', views.UserTokenView.as_view()),
    url(r'^notifications-feed/(?P<page>.+)/$', views.NotificationsFeedView.as_view()),
    url(r'^enrich-notification/', views.EnrichNotificationView.as_view()),

]
