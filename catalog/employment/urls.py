from django.conf.urls import url
from catalog.employment import views

urlpatterns = [
    url(r'^create-user-employment/', views.CreateUserEmploymentView.as_view()),
    url(r'^update-user-employment/(?P<pk>.+)/$', views.UpdateUserEmploymentView.as_view()),
    url(r'^update-user-employment-in-language/(?P<pk>.+)/(?P<language>.+)/$', views.UpdateUserEmploymentInLanguageView.as_view()),
    url(r'^delete-user-employment/(?P<pk>.+)/$', views.DeleteUserEmploymentView.as_view()),
    url(r'^get-user-employment-details/(?P<pk>.+)/$', views.UserEmploymentDetailsView.as_view()),
    url(r'^get-user-employments/(?P<profile>.+)/(?P<education>.+)/(?P<language>.+)/$', views.UserEmploymentsView.as_view()),
]
