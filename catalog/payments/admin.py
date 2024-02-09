from django.contrib import admin
from hvad.admin import TranslatableAdmin
from .models import *


class PaymentProductAdmin(TranslatableAdmin):
    list_display = ['id', 'code']
    raw_id_fields = ('unit_type',)
    search_fields = ['code']

    class Meta:
        model = PaymentProduct


admin.site.register(PaymentProduct, PaymentProductAdmin)


class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ['default_name', 'price_uah', 'price_usd']
    raw_id_fields = ('product', 'category', 'country',)
    search_fields = ['default_name']

    class Meta:
        model = ProductPrice


admin.site.register(ProductPrice, ProductPriceAdmin)


class PaymentOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'account', 'create_date', 'sum']

    class Meta:
        model = PaymentOrder


admin.site.register(PaymentOrder, PaymentOrderAdmin)


class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = [field.name for field in PaymentAccount._meta.fields]

    class Meta:
        model = PaymentAccount


admin.site.register(PaymentAccount, PaymentAccountAdmin)


class PaymentAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Payment._meta.fields]

    class Meta:
        model = Payment


admin.site.register(Payment, PaymentAdmin)
