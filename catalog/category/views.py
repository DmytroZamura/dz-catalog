from __future__ import unicode_literals
from .serializers import *
from rest_framework import generics
from .models import Category
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page



class CategoryChildSet(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer

    @method_decorator(cache_page(60 * 20))
    def dispatch(self, *args, **kwargs):
        return super(CategoryChildSet, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        parent = int(self.kwargs['parent'])
        # content_exists = self.request.GET.get('content_exists', None)
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)

        filter_list = Q()

        if posts_exist is not None:
            filter_list = filter_list & Q(posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(communities_exist=True)

        if parent == 0:
            filter_list = filter_list & Q(first_level=True)
        else:
            filter_list = filter_list & Q(parent=parent)

        # if content_exists:
        #     filter_list = filter_list & Q(content_exists=True)

        objects = Category.objects.language().fallbacks('en').filter(filter_list).order_by('position')

        return objects


class CategoryParentSet(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategoryParentSerializer

    def get_object(self):
        id = int(self.kwargs['id'])
        return Category.objects.language().fallbacks('en').get(pk=id)


class Categories(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.language().fallbacks('en').all()


class CategoryDetails(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Category.objects.language().fallbacks('en').all()
    serializer_class = CategorySerializer


class CategoriesSearch(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = CategorySerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(CategoriesSearch, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.kwargs['name']
        posts_exist = self.request.GET.get('posts_exist', None)
        companies_exist = self.request.GET.get('companies_exist', None)
        products_exist = self.request.GET.get('products_exist', None)
        users_exist = self.request.GET.get('users_exist', None)
        communities_exist = self.request.GET.get('communities_exist', None)

        filter_list = Q()

        if posts_exist is not None:
            filter_list = filter_list & Q(posts_exist=True)
        if companies_exist is not None:
            filter_list = filter_list & Q(companies_exist=True)
        if products_exist is not None:
            filter_list = filter_list & Q(products_exist=True)
        if users_exist is not None:
            filter_list = filter_list & Q(users_exist=True)
        if communities_exist is not None:
            filter_list = filter_list & Q(communities_exist=True)
        if name:
            filter_list = filter_list & Q(name__icontains=name)

        objects = Category.objects.language().filter(filter_list).order_by('parent', 'name')

        if not objects:
            objects = Category.objects.language('en').filter(filter_list).order_by(
                'parent', 'name')

        return objects


class CategoryAttributes(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CategoryAttributeSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(CategoryAttributes, self).dispatch(*args, **kwargs)
    def get_queryset(self):
        category = int(self.kwargs['category'])

        return CategoryAttribute.objects.filter(category=category).order_by('position')


class CreateSuggestedCategoryView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = SuggestedCategory.objects.all()
    serializer_class = SuggestedCategorySerializer
