from django.conf.urls import url
from catalog.company import views

urlpatterns = [
    url(r'^get-company-types/', views.CompanyTypesView.as_view()),
    url(r'^get-company-sizes/', views.CompanySizesView.as_view()),
    url(r'^get-company-industries/', views.CompanyIndustriesView.as_view()),
    url(r'^get-company-by-slug/(?P<slug>.+)/$', views.CompanyBySlugView.as_view()),
    url(r'^get-company-by-slug-in-language/(?P<slug>.+)/(?P<language>.+)/$',
        views.CompanyBySlugInLanguageView.as_view()),
    url(r'^get-company-categories/(?P<company>.+)/(?P<parent>.+)/(?P<interest>.+)/$',
        views.CompanyCategoriesView.as_view()),
    url(r'^create-company-category/', views.CreateCompanyCategoryView.as_view()),
    url(r'^get-company-details/(?P<pk>[0-9]+)/$', views.CompanyDetailsView.as_view()),
    url(r'^get-company-details-short/(?P<pk>[0-9]+)/$', views.CompanyDetailsShortView.as_view()),
    url(r'^get-company-details-in-language/(?P<pk>[0-9]+)/(?P<language>.+)/$',
        views.CompanyDetailsInLanguageView.as_view()),
    url(r'^update-company-details/(?P<pk>[0-9]+)/(?P<language>.+)/$', views.UpdateCompanyDetailsView.as_view()),
    url(r'^delete-company/(?P<pk>[0-9]+)/$', views.DeleteCompanyView.as_view()),
    url(r'^create-company/', views.CreateCompanyView.as_view()),
    url(r'^check-delete-company-admin-status/', views.CheckDeleteCompanyAdminStatusView.as_view()),
    url(r'^companies-by-page/(?P<page>[0-9]+)/$', views.CompaniesByPageView.as_view()),
    url(r'^companies-count/', views.CompaniesCountView.as_view()),
    url(r'^get-companies-by-name/(?P<name>.+)/(?P<language>.+)/$', views.CompaniesByNameView.as_view()),
    url(r'^search-companies-by-name/(?P<name>.+)/$', views.SearchCompaniesByNameView.as_view()),
    url(r'^get-company-users/(?P<company>.+)/$', views.CompanyUsersView.as_view()),
    url(r'^get-user-companies/(?P<user>.+)/$', views.UserCompaniesView.as_view()),
    url(r'^get-adminuser-companies-not-in-community/(?P<user>.+)/(?P<community>.+)/$',
        views.UserCompaniesNotInCommunityView.as_view()),
    url(r'^get-adminuser-companies-in-community/(?P<user>.+)/(?P<community>.+)/$',
        views.UserCompaniesInCommunityView.as_view()),

    url(r'^get-user-company-admin-permisions/(?P<user>.+)/(?P<company>.+)/$', views.UserPermisionsView.as_view()),
    url(r'^create-company-user/', views.CreateCompanyUserView.as_view()),
    url(r'^company-user-update/(?P<company>.+)/(?P<user>.+)/$', views.CompanyUserUpdateView.as_view()),
    url(r'^get-company-followers/(?P<company>.+)/$', views.CompanyFollowersView.as_view()),
    url(r'^get-following-companies/(?P<user>.+)/$', views.FollowingCompaniesView.as_view()),
    url(r'^follow-company/', views.FollowCompanyView.as_view()),
    url(r'^unfollow-company/(?P<user>.+)/(?P<company>.+)/$', views.UnfollowCompanyView.as_view()),
    url(r'^check-following-company/', views.CheckFollowingCompany.as_view()),
    url(r'^check-company-by-slug/', views.CheckCompanyBySlugView.as_view()),
    url(r'^create-favorite-company/', views.CreateFavoriteCompanyView.as_view()),
    url(r'^delete-favorite-company/(?P<company>[0-9]+)/$', views.DeleteFavoriteCompanyView.as_view()),
    url(r'^favorite-companies-by-page/(?P<page>[0-9]+)/$', views.FavoriteCompaniesByPageView.as_view()),




]
