from __future__ import absolute_import
from __future__ import unicode_literals
from django.contrib import admin
from .models import Product, ProductImage, ProductCategory, ProductGroup, ProductGroupItem, ProductAttribute, \
    ProductAttributeValue, FavoriteProduct, ProductEventsQty, ProductSEOData
from catalog.general.models import Country, Currency, UnitType
from catalog.company.models import Company
from hvad.admin import TranslatableAdmin, TranslatableModelForm


class ProductAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        self.fields['origin'].queryset = Country.objects.language('en').all()
        self.fields['origin'].label_from_instance = lambda obj: obj.name
        self.fields['company'].queryset = Company.objects.language('en').all()
        self.fields['company'].label_from_instance = lambda obj: obj.name

        self.fields['unit_type'].queryset = UnitType.objects.language().all()
        self.fields['unit_type'].label_from_instance = lambda obj: obj.name

        self.fields['currency'].queryset = Currency.objects.language().all()
        self.fields['currency'].label_from_instance = lambda obj: obj.name


class ProductAdmin(TranslatableAdmin):
    form = ProductAdminForm

    list_display = ['id', 'slug', 'model_number', 'brand_name',
                    'product_or_service',
                    'published', 'price_from', 'price_to', 'one_price']
    raw_id_fields = ('category', )
    search_fields = ['slug']

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)


class ProductGroupAdminForm(TranslatableModelForm):
    def __init__(self, *args, **kwargs):
        super(ProductGroupAdminForm, self).__init__(*args, **kwargs)

        self.fields['company'].queryset = Company.objects.language('en').all()
        self.fields['company'].label_from_instance = lambda obj: obj.name


class ProductGroupAdmin(TranslatableAdmin):
    form = ProductGroupAdminForm

    list_display = ['id', 'child_qty']

    class Meta:
        model = ProductGroup


admin.site.register(ProductGroup, ProductGroupAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductImage._meta.fields]

    class Meta:
        model = ProductImage


admin.site.register(ProductImage, ProductImageAdmin)


class ProductSEODataAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductSEOData._meta.fields]

    class Meta:
        model = ProductSEOData


admin.site.register(ProductSEOData, ProductSEODataAdmin)


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductCategory._meta.fields]

    class Meta:
        model = ProductCategory


admin.site.register(ProductCategory, ProductCategoryAdmin)


class ProductGroupItemAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductGroupItem._meta.fields]

    class Meta:
        model = ProductGroupItem


admin.site.register(ProductGroupItem, ProductGroupItemAdmin)


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductAttribute._meta.fields]

    class Meta:
        model = ProductAttribute


admin.site.register(ProductAttribute, ProductAttributeAdmin)


class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductAttributeValue._meta.fields]

    class Meta:
        model = ProductAttributeValue


admin.site.register(ProductAttributeValue, ProductAttributeValueAdmin)



class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FavoriteProduct._meta.fields]

    class Meta:
        model = FavoriteProduct


admin.site.register(FavoriteProduct, FavoriteProductAdmin)


class ProductEventsQtyAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductEventsQty._meta.fields]

    class Meta:
        model = ProductEventsQty


admin.site.register(ProductEventsQty, ProductEventsQtyAdmin)

