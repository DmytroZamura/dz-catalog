from django.conf.urls import url
from catalog.category import views

urlpatterns = [
    url(r'^category/(?P<pk>.+)/$', views.CategoryDetails.as_view()),
    url(r'^category-child-set/(?P<parent>[0-9]+)/$', views.CategoryChildSet.as_view()),
    url(r'^category-parent-set/(?P<id>[0-9]+)/$', views.CategoryParentSet.as_view()),
    url(r'^categories/$', views.Categories.as_view()),
    url(r'^categories-search/(?P<name>.+)/$', views.CategoriesSearch.as_view()),
    url(r'^get-category-attributes/(?P<category>[0-9]+)/$', views.CategoryAttributes.as_view()),
    url(r'^create-suggested-category/', views.CreateSuggestedCategoryView.as_view()),
]
