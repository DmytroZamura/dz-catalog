from django.conf.urls import url
from catalog.attribute import views

urlpatterns = [
    url(r'^attributes-search/(?P<name>.+)/$', views.AttributesSearch.as_view()),
    url(r'^get-attribute-values/(?P<attribute>[0-9]+)/$', views.AttributeValues.as_view()),
]
