from .serializers import ProductImageSerializer, ProductShortSerializer, ProductSerializer, ProductGroupSerializer, \
    FavoriteProductSerializer
from rest_framework import generics
from .models import Product, ProductImage, ProductGroup, FavoriteProduct
from catalog.company.models import Company
from catalog.user_profile.models import UserProfile
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from catalog.general.models import convert_price
import json
from .permissions import IsOwnerOrCompanyAdmin, IsOwnerOrCompanyAdminDetails, IsOwner
from .documents import ProductDocument
# from elasticsearch_dsl import Q as Qel
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from catalog.general.models import CurrencyRate
from django.core.exceptions import ObjectDoesNotExist


def get_ordering(code, parent_model=''):
    if parent_model == 'product__':
        ordering = ['-create_date']
    else:
        ordering = ['-' + parent_model + 'update_date', '-' + parent_model + 'eventsqty__rating',
                    '-' + parent_model + 'eventsqty__related_reviews', '-id']
    if code == '-price':
        ordering = ['-' + parent_model + 'price_usd_to', '-' + parent_model + 'eventsqty__rating',
                    '-' + parent_model + 'eventsqty__related_reviews', '-' + parent_model + 'update_date', '-id']
    if code == 'price':
        ordering = [parent_model + 'price_usd_to', '-' + parent_model + 'eventsqty__rating',
                    '-' + parent_model + 'eventsqty__related_reviews', '-' + parent_model + 'update_date', '-id']
    if code == 'discounts':
        ordering = [parent_model + 'discount', '-' + parent_model + 'eventsqty__rating',
                    '-' + parent_model + 'eventsqty__related_reviews', '-' + parent_model + 'update_date', '-id']
    if code == 'rating':
        ordering = ['-' + parent_model + 'eventsqty__rating', '-' + parent_model + 'eventsqty__related_reviews',
                    '-' + parent_model + 'update_date', '-id']
    if code == 'popularity':
        ordering = ['-' + parent_model + 'eventsqty__related_reviews',
                    '-' + parent_model + 'eventsqty__related_questions', '-' + parent_model + 'eventsqty__rating',
                    '-' + parent_model + 'update_date', '-id']

    return ordering


def get_elastic_ordering(code, latitude=0, longitude=0):
    ordering = ['-update_date', '-rating', '-related_reviews']
    if code == '-price':
        ordering = ['-price_usd_to', '-rating', '-related_reviews', '-update_date']
    if code == 'price':
        ordering = ['price_usd_to', '-rating', '-related_reviews', '-update_date']
    if code == 'discounts':
        ordering = ['discount', '-rating', '-related_reviews', '-update_date']
    if code == 'rating':
        ordering = ['-rating', '-related_reviews', '-update_date']
    if code == 'popularity':
        ordering = ['-related_reviews', '-related_questions', '-rating', '-update_date']
    if code == 'close':
        ordering = [{'_geo_distance': {
            'location': {'lat': latitude, 'lon': longitude},
            "order": "asc",
            "unit": "km",
            "distance_type": "arc",
            "ignore_unmapped": "true"
        }}, '-related_reviews', '-related_questions', '-rating']

    return ordering


class DeleteProductView(APIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)

    def delete(self, request, pk):
        product = Product.objects.language('en').get(pk=pk)
        self.check_object_permissions(self.request, product)

        product.smart_delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateProductGroupView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = ProductGroupSerializer
    queryset = ProductGroup.objects.language().all()

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}


class UpdateProductGroupView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = ProductGroupSerializer

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        object = ProductGroup.objects.language(language).fallbacks('en').get(pk=pk)
        self.check_object_permissions(self.request, object)
        return object


class DeleteProductGroupView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    serializer_class = ProductGroupSerializer
    queryset = ProductGroup.objects.language().fallbacks('en').all()


class SearchCompanyProductGroupsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductGroupSerializer

    def get_queryset(self):
        company = self.kwargs['company']
        name = self.kwargs['name']

        if name == 'null':
            objects = ProductGroup.objects.language().fallbacks('en').filter(company=company).order_by('name')
        else:
            objects = ProductGroup.objects.language().fallbacks('en').filter(company=company,
                                                                             name__icontains=name).order_by('name')
        return objects


class SearchUserProductGroupsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductGroupSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        name = self.kwargs['name']
        if name == 'null':
            objects = ProductGroup.objects.language().fallbacks('en').filter(user=user).order_by('name')
        else:
            objects = ProductGroup.objects.language().fallbacks('en').filter(user=user, name__icontains=name).order_by(
                'name')
        return objects


class CompanyChildProductGroupsView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = ProductGroupSerializer

    def get_queryset(self):
        company = self.kwargs['company']
        parent = int(self.kwargs['parent'])
        language = self.kwargs['language']
        if parent == 0:
            return ProductGroup.objects.language(language).fallbacks('en').filter(parent__isnull=True, company=company)
        else:
            return ProductGroup.objects.language(language).fallbacks('en').filter(parent=parent, company=company)


class UserChildProductGroupsView(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = ProductGroupSerializer

    def get_queryset(self):
        user = self.kwargs['user']
        parent = int(self.kwargs['parent'])
        language = self.kwargs['language']
        if parent == 0:
            return ProductGroup.objects.language(language).fallbacks('en').filter(parent__isnull=True, user=user)
        else:
            return ProductGroup.objects.language(language).fallbacks('en').filter(parent=parent, user=user)


class ProductImagesView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductImageSerializer

    def get_queryset(self):
        product = self.kwargs['product']
        return ProductImage.objects.filter(product=product).order_by('position')


class ProductImageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductImageSerializer

    def get_object(self):
        product = self.kwargs['product']
        return ProductImage.objects.filter(product=product).order_by('position').first()


class CreateProductImageView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdminDetails)
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()


class DeleteProductImageView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdminDetails)
    serializer_class = ProductImageSerializer
    queryset = ProductImage.objects.all()


class UserProductsView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):
        user = self.kwargs['user']

        return Product.objects.filter(user_id=user, deleted=False)


class UserProductsByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):

        user = self.kwargs['user']
        page = int(self.kwargs['page'])

        if page == 0:
            products = Product.objects.language().filter(user_id=user, deleted=False)[:20]
        else:

            item_from = page * 20
            item_to = page * 20 + 20
            products = Product.objects.language().filter(user_id=user, deleted=False)[item_from:item_to]
        return products


class UserProductsByPageDefaultLangView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):

        user = self.kwargs['user']
        page = int(self.kwargs['page'])

        if page == 0:
            products = Product.objects.language('en').filter(user_id=user, deleted=False).exclude(
                id__in=Product.objects.language().filter(user_id=user, deleted=False))[:20]
        else:

            item_from = page * 20
            item_to = page * 20 + 20
            products = Product.objects.language('en').filter(user_id=user, deleted=False).exclude(
                id__in=Product.objects.language().filter(user_id=user, deleted=False))[item_from:item_to]
        return products


class ProductsByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductShortSerializer

    @method_decorator(cache_page(60 * 10))
    def dispatch(self, *args, **kwargs):
        return super(ProductsByPageView, self).dispatch(*args, **kwargs)

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)

        try:
            rate_usd = CurrencyRate.objects.get(currency=int(current_currency), currency_to=1)
            rate = rate_usd.rate

        except ObjectDoesNotExist:
            rate = None

        return {'request': self.request, 'current_currency': current_currency, 'rate_usd': rate}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        user = self.request.GET.get('user', None)
        category = self.request.GET.get('category', None)
        community = self.request.GET.get('community', None)
        published = self.request.GET.get('published', None)
        origin = self.request.GET.get('origin', None)
        product_or_service = self.request.GET.get('product_or_service', None)
        unit_type = self.request.GET.get('unit_type', None)
        currency = self.request.GET.get('currency', None)
        company = self.request.GET.get('company', None)
        product_group = self.request.GET.get('product_group', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        pricefrom = self.request.GET.get('pricefrom', None)
        priceto = self.request.GET.get('priceto', None)
        attributes = self.request.GET.get('attributes', None)
        tag = self.request.GET.get('tag', None)
        keyword = self.request.GET.get('keyword', None)
        latitude = self.request.GET.get('latitude', None)
        longitude = self.request.GET.get('longitude', None)
        ordering = self.request.GET.get('ordering', None)

        # if (keyword is not None) or ordering == 'close':
        #
        #     s = ProductDocument.search()
        #     if keyword is not None:
        #         filter_list = Q(name_inicontain=keyword) | Q(description_inicontain=keyword) | Q(brand_name_inicontain=keyword)\
        #             | Q(price_conditions_inicontain=keyword)| Q(packaging_and_delivery_inicontain=keyword)
        #     else:
        #         filter_list = Q()
        #
        #     filter_list = filter_list & Q(published=True)
        #     filter_list = filter_list & Q(deleted=False)
        #
        #     if country is not None:
        #         filter_list = filter_list & Q(country=country)
        #     if region is not None:
        #         filter_list = filter_list & Q(region=region)
        #     if city is not None:
        #         filter_list = filter_list & Q(city=city)
        #     if category is not None:
        #         filter_list = filter_list & Q(category=category)
        #
        #     ordering_code = get_elastic_ordering(ordering, latitude, longitude)
        #     s = s.query(filter_list).sort(*ordering_code)
        #
        #     if page == 0:
        #         s = s[:20]
        #     else:
        #         item_from = page * 20
        #         item_to = page * 20 + 20
        #         s = s[item_from:item_to]
        #
        #     response = s.execute()
        #
        #     response_dict = response.to_dict()
        #     hits = response_dict['hits']['hits']
        #     products = []
        #     for hit in hits:
        #         try:
        #             obj = Product.objects.language().fallbacks('en').get(id=hit['_id'])
        #             products.append(obj)
        #         except Product.DoesNotExist:
        #             pass
        #
        #     # ids = [hit['_id'] for hit in hits]
        #     # ordering_code = get_ordering(ordering)
        #     # products = Product.objects.language().fallbacks('en').filter(id__in=ids).order_by(*ordering_code)

        filter_list = Q()
        filter_list = filter_list & Q(deleted=False)
        if keyword is not None:
            filter_list = filter_list & (
                    Q(name__icontains=keyword) | Q(short_description__icontains=keyword) | Q(brand_name__icontains=keyword))

        if user is not None:
            filter_list = filter_list & Q(user=user, company=None)
        if company is not None:
            filter_list = filter_list & Q(company=company)
        if category is not None:
            filter_list = filter_list & Q(product_categories__category=category)

        if int(published) > 0:
            filter_list = filter_list & Q(published=True)

        if origin is not None:
            filter_list = filter_list & Q(origin=origin)
        if country is not None:
            filter_list = filter_list & (Q(user__user_profile__country=country) | Q(company__country=country))
        if city is not None:
            filter_list = filter_list & (Q(user__user_profile__city=city) | Q(company__city=city))
        if region is not None:
            filter_list = filter_list & (
                    Q(user__user_profile__city__region=region) | Q(company__city__region=region))
        if product_or_service is not None:
            filter_list = filter_list & Q(product_or_service=product_or_service)
        if unit_type is not None:
            filter_list = filter_list & Q(unit_type=unit_type)
        if currency is not None:
            filter_list = filter_list & Q(currency=currency)
        if product_group is not None:
            filter_list = filter_list & Q(product_groups__group=product_group)
        if community is not None:
            filter_list = filter_list & Q(company__communities__community=community)
        if tag is not None:
            tag = tag.lower()
            filter_list = filter_list & Q(tags__name__iexact=tag)

        if currency is not None:
            if pricefrom is not None:
                price = convert_price(int(pricefrom), int(currency), 1)
                filter_list = filter_list & Q(price_usd_to__gte=price)

            if priceto is not None:
                price = convert_price(int(priceto), int(currency), 1)
                filter_list = filter_list & Q(price_usd_to__lte=price)

        products = Product.objects.language().fallbacks('en').filter(filter_list)

        if attributes is not None:
            attributes = json.loads(attributes)
            for attribute in attributes:
                type = attribute.get('type')
                multiple = attribute.get('multiple')
                id = attribute.get('attribute')
                if type == 1 and multiple == False:
                    value_list = attribute.get('value_list')
                    products = products.filter(attributes__attribute=id, attributes__values__value_list=value_list)

                if type == 1 and multiple == True:
                    multiple_values = attribute.get('values')
                    for value in multiple_values:
                        products = products.filter(attributes__attribute=id, attributes__values__value_list=value)

                if type == 4:
                    products = products.filter(attributes__attribute=id, attributes__values__value_boolean=True)

                if type == 2 or type == 5:
                    min_max_values = attribute.get('values')
                    if type == 2:
                        products = products.filter(attributes__attribute=id,
                                                   attributes__values__value_number__gte=min_max_values[0],
                                                   attributes__values__value_number__lte=min_max_values[1])
                    if type == 5:
                        products = products.filter(attributes__attribute=id,
                                                   attributes__values__value_integer__gte=min_max_values[0],
                                                   attributes__values__value_integer__lte=min_max_values[1])

        ordering_code = get_ordering(ordering)

        if page == 0:
            products = products.order_by(*ordering_code)[:20]
        else:
            item_from = page * 20
            item_to = page * 20 + 20
            products = products.order_by(*ordering_code)[item_from:item_to]

        return products


class CurrentUserProductsByPageView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):
        user = self.request.user
        page = int(self.kwargs['page'])

        if page == 0:
            products = Product.objects.language().filter(user_id=user, deleted=False)[:20]
        else:

            item_from = page * 20
            item_to = page * 20 + 20
            products = Product.objects.language().filter(user_id=user, deleted=False)[item_from:item_to]
        return products


class ProductDetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Product.objects.language().fallbacks('en').filter(deleted=False)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}


class ProductBySlugView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_object(self):

        slug = self.kwargs['slug']
        sslug = self.kwargs['sslug']
        subject = self.kwargs['subject']

        if subject == 'c':
            company = Company.objects.untranslated().get(slug=sslug)
            print(company.id)
            product = Product.objects.language().fallbacks('en').get(company=company, slug__iexact=slug, published=True)
        else:
            profile = UserProfile.objects.untranslated().get(slug=sslug)
            product = Product.objects.language().fallbacks('en').get(user=profile.user, slug__iexact=slug,
                                                                     published=True)

        return product


class ProductDetailsInLanguageView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        object = Product.objects.language(language).fallbacks('en').get(pk=pk, deleted=False)
        return object


class UpdateProductDetailsView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)

    serializer_class = ProductSerializer

    def get_serializer_context(self):
        current_currency = self.kwargs.get('current_currency', None)
        return {'request': self.request, 'current_currency': current_currency}

    def get_object(self):
        language = self.kwargs['language']
        pk = self.kwargs['pk']
        obj = Product.objects.language(language).fallbacks('en').get(pk=pk, deleted=False)
        self.check_object_permissions(self.request, obj)
        return obj


class CreateProductView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwnerOrCompanyAdmin)
    queryset = Product.objects.language().all()
    serializer_class = ProductSerializer


class CreateFavoriteProductView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer

    def get_serializer_context(self):
        return {'request': self.request, 'current_currency': None}


class DeleteFavoriteProductView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = FavoriteProductSerializer

    def get_object(self):
        product = self.kwargs['product']
        obj = FavoriteProduct.objects.get(product=product, user=self.request.user)
        self.check_object_permissions(self.request, obj)

        return obj


class FavoriteProductsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteProductSerializer

    def get_serializer_context(self):
        current_currency = self.request.GET.get('current_currency', 1)
        return {'request': self.request, 'current_currency': current_currency}

    def get_queryset(self):

        page = int(self.kwargs['page'])
        category = self.request.GET.get('category', None)
        origin = self.request.GET.get('origin', None)
        product_or_service = self.request.GET.get('product_or_service', None)
        unit_type = self.request.GET.get('unit_type', None)
        currency = self.request.GET.get('currency', None)
        product_group = self.request.GET.get('product_group', None)
        country = self.request.GET.get('country', None)
        city = self.request.GET.get('city', None)
        region = self.request.GET.get('region', None)
        pricefrom = self.request.GET.get('pricefrom', None)
        priceto = self.request.GET.get('priceto', None)
        attributes = self.request.GET.get('attributes', None)
        ordering = self.request.GET.get('ordering', None)

        filter_list = Q(user=self.request.user)
        filter_list = filter_list & Q(product__deleted=False, product__published=True)

        if category is not None:
            filter_list = filter_list & Q(product__product_categories__category=category)

        if origin is not None:
            filter_list = filter_list & Q(product__origin=origin)
        if country is not None:
            filter_list = filter_list & (
                    Q(product__user__user_profile__country=country) | Q(product__company__country=country))
        if city is not None:
            filter_list = filter_list & (Q(product__user__user_profile__city=city) | Q(product__company__city=city))
        if region is not None:
            filter_list = filter_list & (
                    Q(product__user__user_profile__city__region=region) | Q(product__company__city__region=region))
        if product_or_service is not None:
            filter_list = filter_list & Q(product__product_or_service=product_or_service)
        if unit_type is not None:
            filter_list = filter_list & Q(product__unit_type=unit_type)
        if currency is not None:
            filter_list = filter_list & Q(product__currency=currency)
        if product_group is not None:
            filter_list = filter_list & Q(product__product_groups__group=product_group)

        if currency is not None:
            if pricefrom is not None:
                price = convert_price(int(pricefrom), int(currency), 1)
                filter_list = filter_list & Q(product__price_usd_to__gte=price)

            if priceto is not None:
                price = convert_price(int(priceto), int(currency), 1)
                filter_list = filter_list & Q(product__price_usd_to__lte=price)

        products = FavoriteProduct.objects.filter(filter_list)

        if attributes is not None:
            attributes = json.loads(attributes)
            for attribute in attributes:
                type = attribute.get('type')
                multiple = attribute.get('multiple')
                id = attribute.get('attribute')
                if type == 1 and multiple == False:
                    value_list = attribute.get('value_list')
                    products = products.filter(product__attributes__attribute=id,
                                               product__attributes__values__value_list=value_list)

                if type == 1 and multiple == True:
                    multiple_values = attribute.get('values')
                    for value in multiple_values:
                        products = products.filter(product__attributes__attribute=id,
                                                   product__attributes__values__value_list=value)

                if type == 4:
                    products = products.filter(product__attributes__attribute=id,
                                               product__attributes__values__value_boolean=True)

                if type == 2 or type == 5:
                    min_max_values = attribute.get('values')
                    if type == 2:
                        products = products.filter(product__attributes__attribute=id,
                                                   product__attributes__values__value_number__gte=min_max_values[0],
                                                   product__attributes__values__value_number__lte=min_max_values[1])
                    if type == 5:
                        products = products.filter(product__attributes__attribute=id,
                                                   product__attributes__values__value_integer__gte=min_max_values[0],
                                                   product__attributes__values__value_integer__lte=min_max_values[1])
        ordering_code = get_ordering(ordering, 'product__')

        if page == 0:
            products = products.order_by(*ordering_code)[:20]
        else:
            item_from = page * 20
            item_to = page * 20 + 20
            products = products.order_by(*ordering_code)[item_from:item_to]

        return products
