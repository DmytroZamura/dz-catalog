from django.conf.urls import url
from catalog.payments import views

urlpatterns = [
    url(r'^get-payment-product-price/(?P<code>.+)/$',
        views.ProductPriceView.as_view()),
    url(r'^get-payment-product-price-by-object/(?P<code>.+)/(?P<id>.+)/$',
        views.ProductPriceForObjectView.as_view()),
    url(r'^check-payments-accounts/',
        views.CheckPaymentAccounts.as_view()),
    url(r'^get-payments/(?P<page>.+)/$',
        views.PaymentsByPageView.as_view()),
    url(r'^get-payment-orders/(?P<page>.+)/$',
        views.PaymentOrdersByPageView.as_view()),
    url(r'^get-payment-account/(?P<id>.+)/$',
        views.PaymentAccountView.as_view()),
    url(r'^get-payments-accounts/',
        views.PaymentAccountsView.as_view()),
    url(r'^create-payment/',
        views.CreatePaymentView.as_view()),
    url(r'^create-payment-order/',
        views.CreateOrderView.as_view()),
    url(r'^payment-callback/',
        views.PaymentCallbackView.as_view()),

]
