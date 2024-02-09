from django.conf.urls import url
from catalog.user_profile import views

urlpatterns = [
    url(r'^delete-user-profile/', views.DeleteUserProfileView.as_view()),
    url(r'^profile/(?P<language>.+)/$', views.UserProfileDetailsView.as_view()),
    url(r'^get-profile/(?P<user>.+)/$', views.ProfileView.as_view(), name='get-profile'),
    url(r'^user-settings/', views.UserSettingsView.as_view()),
    url(r'^get-short-user-profile/(?P<user>.+)/$', views.ShortUserProfileView.as_view()),
    url(r'^get-short-user-profile-by-slug/(?P<slug>.+)/$', views.ShortUserProfileBySlugView.as_view()),
    url(r'^search-profiles-by-name/(?P<name>.+)/$', views.SearchProfilesByNameView.as_view()),
    url(r'^suggestions/(?P<keyword>.+)/$', views.SuggestionsView.as_view()),
    url(r'^profile-check/(?P<userauth>.+)/(?P<locale>.+)/$', views.UserProfileCheckView.as_view()),
    url(r'^profile-image-upload/(?P<filename>.+)/$', views.UserProfileImageUploadView.as_view()),
    url(r'^delete-profile-category/(?P<profile>.+)/(?P<category>.+)/$', views.DeleteUserProfileCategoryView.as_view()),
    url(r'^create-profile-category/', views.CreateUserProfileCategoryView.as_view()),
    url(r'^get-profile-categories/(?P<profile>.+)/(?P<interest>.+)/$', views.UserProfileCategoriesView.as_view()),
    url(r'^get-child-profile-categories/(?P<profile>.+)/(?P<parent>.+)/(?P<interest>.+)/$',
        views.ChildUserProfileCategoriesView.as_view()),
    url(r'^get-all-profile-categories/(?P<profile>.+)/(?P<interest>.+)/$',
        views.AllUserProfileCategoriesView.as_view()),
    url(r'^get_profile-categories-for-select/(?P<profile>.+)/(?P<interest>.+)/(?P<name>.+)/$',
        views.ProfileCategoriesForSelectView.as_view()),
    url(r'^get-profile-country-interests/(?P<profile>.+)/$', views.UserProfileCountryInterestsView.as_view()),
    url(r'^create-profile-country-interest/', views.CreateUserProfileCountryInterestView.as_view()),
    url(r'^delete-profile-country-interest/(?P<profile>.+)/(?P<country>.+)/$',
        views.DeleteUserProfileCountryInterestView.as_view()),
    url(r'^profiles-by-page/(?P<page>[0-9]+)/$', views.UserProfilesByPageView.as_view()),
    url(r'^profiles-count/', views.UserProfilesCountView.as_view()),
    url(r'^check-profile-slug/(?P<slug>.+)/$', views.CheckProfileSlugView.as_view()),
    url(r'^get-profile-followers/(?P<profile>.+)/$', views.UserProfileFollowersView.as_view()),
    url(r'^get-following-profiles/(?P<user>.+)/$', views.FollowingUserProfilesView.as_view()),
    url(r'^follow-profile/', views.FollowUserProfileView.as_view(), name='follow-profile'),
    url(r'^unfollow-profile/(?P<user>.+)/(?P<profile>.+)/$', views.UnfollowUserProfileView.as_view()),
    url(r'^check-following-profile/', views.CheckFollowingUserProfile.as_view()),
    url(r'^set-seen-profile-notifications/', views.SetSeenNotificationsView.as_view()),
    url(r'^create-resume/', views.CreateResumeView.as_view()),
    url(r'^delete-resume/(?P<pk>[0-9]+)/$', views.DeleteResumeView.as_view()),
    url(r'^profile-resumes/', views.ProfileResumesView.as_view()),
    url(r'^profile-allowed-resumes/(?P<profile>.+)/$', views.ProfileAllowedResumesView.as_view()),
    url(r'^set-resume-public-status/(?P<pk>.+)/(?P<status>.+)/$', views.SetResumePublicStatus.as_view()),
    url(r'^get-total-events-qty/', views.TotalEventsQtyView.as_view()),


]
