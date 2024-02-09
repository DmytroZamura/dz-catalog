from django.conf.urls import url
from catalog.file import views


urlpatterns = [

    url(r'^file/(?P<pk>.+)/$', views.FileDetailsView.as_view()),
    url(r'^files/', views.FilesView.as_view()),
    url(r'^file-upload/(?P<filename>.+)/(?P<filetype>.+)/$', views.FileUploadView.as_view()),
    url(r'^image-upload/(?P<filename>.+)/(?P<filetype>.+)/$', views.ImageUploadView.as_view())
]
