from django.conf.urls import url
from catalog.supply_request import views

urlpatterns = [

    url(r'^create-supply-request/', views.CreateSupplyRequestView.as_view()),
    url(r'^new-supply-request/', views.NewSupplyRequestView.as_view()),
    url(r'^update-supply-request/(?P<pk>[0-9]+)/$', views.UpdateSupplyRequestView.as_view()),
    url(r'^update-supply-request-position/(?P<pk>[0-9]+)/$', views.UpdateSupplyRequestPositionView.as_view()),
    url(r'^delete-supply-request/(?P<pk>[0-9]+)/$', views.DeleteSupplyRequestView.as_view()),
    url(r'^delete-supply-request-position/(?P<pk>[0-9]+)/$', views.DeleteSupplyRequestPositionView.as_view()),
    url(r'^get-supply-request/(?P<pk>[0-9]+)/$', views.SupplyRequestView.as_view()),
    url(r'^get-user-supply-requests/(?P<page>.+)/(?P<order>.+)/$', views.UserSupplyRequestsByPageView.as_view()),
    url(r'^get-user-sales-requests/(?P<page>.+)/(?P<order>.+)/$', views.UserSalesRequestsByPageView.as_view()),
    url(r'^get-company-supply-requests/(?P<company>.+)/(?P<page>.+)/(?P<order>.+)/$',
        views.CompanySupplyRequestsByPageView.as_view()),
    url(r'^get-company-sales-requests/(?P<company>.+)/(?P<page>.+)/(?P<order>.+)/$',
        views.CompanySalesRequestsByPageView.as_view()),
    url(r'^supply-request-statuses/', views.SupplyRequestStatusListView.as_view()),
    url(r'^update-supply-request-comment/(?P<req>[0-9]+)/$', views.UpdateRequestCommentView.as_view()),
    url(r'^update-supply-request-charges/(?P<req>[0-9]+)/$', views.UpdateRequestChargesView.as_view()),
    url(r'^update-supply-request-status/(?P<req>[0-9]+)/$', views.UpdateRequestStatusView.as_view()),
    url(r'^update-supply-request-status-by-customer/(?P<req>[0-9]+)/$',
        views.UpdateRequestStatusByCustomerView.as_view()),

]
