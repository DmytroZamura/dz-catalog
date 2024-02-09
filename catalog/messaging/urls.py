from django.conf.urls import url
from catalog.messaging import views

urlpatterns = [
    url(r'^get-chats/(?P<page>.+)/$', views.ChatsView.as_view()),
    url(r'^create-message/', views.CreateMessageView.as_view()),
    url(r'^delete-message/(?P<pk>[0-9]+)/$', views.DeleteMessageView.as_view()),
    url(r'^get-message/(?P<pk>[0-9]+)/$', views.MessageView.as_view()),
    url(r'^edit-message/(?P<pk>[0-9]+)/$', views.EditMessageView.as_view()),
    url(r'^get-chat-messages-by-page/(?P<chat>.+)/(?P<page>.+)/$', views.ChatMessagesByPageView.as_view()),
    url(r'^get-chats-count/', views.ChatsCountView.as_view()),
    url(r'^get-unread-messages-count/', views.UnreadMessagesCountView.as_view()),
    url(r'^get-company-unread-messages-count/(?P<company>.+)/$', views.CompanyUnreadMessagesCountView.as_view()),
    url(r'^get-messages-count/(?P<chat>.+)/$', views.MessagesCountView.as_view()),
    url(r'^get-chat-id-for-user-contact/(?P<user>.+)/(?P<contact>.+)/$', views.ChatIdForUserContactView.as_view()),
    url(r'^set-read-messages-for-chat-user/(?P<chat>.+)/$', views.SetReadMessagesForChatUserView.as_view()),
    url(r'^set-read-messages-for-chat-company/(?P<chat>.+)/(?P<company>.+)/$',
        views.SetReadMessagesForChatCompanyView.as_view()),
    url(r'^get-your-participant/(?P<chat>.+)/$', views.YourParticipantView.as_view()),
    url(r'^check-user-actions/', views.CheckUserActions.as_view()),

]
