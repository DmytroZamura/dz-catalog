from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import TagSerializer, TagFollowerSerializer, FavoriteTagSerializer
from django.shortcuts import get_object_or_404
from .models import TagFollower, Tag
from .permissions import IsFollower
from django.db.models import Q

def get_ordering(code, parent_model=''):

    ordering = [parent_model + 'name']

    if code == 'popularity':
        ordering = ['-' + parent_model + 'qty__followers']

    return ordering

class TagBySlugView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def get_object(self):
        slug = self.kwargs['slug']
        obj = get_object_or_404(Tag, name__iexact=slug.lower())
        return obj


class SearchTagsByNameView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def get_queryset(self):
        name = self.kwargs['name']

        objects = Tag.objects.filter(name__icontains=name.lower()).order_by('name')[:10]

        return objects


class FollowTagView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = TagFollower.objects.all()
    serializer_class = TagFollowerSerializer


class UnfollowTagView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, IsFollower)
    serializer_class = TagFollowerSerializer

    def get_object(self):
        user = self.request.user
        tag = self.kwargs['tag']
        object = TagFollower.objects.get(tag=tag, user=user)
        self.check_object_permissions(self.request, object)
        return object

class TagsByPageViewView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def get_queryset(self):
        page = int(self.kwargs['page'])
        keyword = self.request.GET.get('keyword', None)
        ordering = self.request.GET.get('ordering', None)

        filter_list = Q()
        if keyword is not None:
            filter_list = filter_list & Q(name__icontains=keyword.lower())

        ordering_code = get_ordering(ordering)
        objects = Tag.objects.filter(filter_list).order_by(*ordering_code)

        if page == 0:
            objects = objects[:20]
        else:
            item_from = page * 20
            item_to = page * 20 + 20
            objects = objects[item_from:item_to]

        return objects

class FavoriteTagsByPageView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteTagSerializer

    def get_queryset(self):

        page = int(self.kwargs['page'])
        keyword = self.request.GET.get('keyword', None)
        ordering = self.request.GET.get('ordering', None)

        filter_list = Q(user=self.request.user)

        if keyword is not None:
            filter_list = filter_list & Q(tag__name__icontains=keyword)

        ordering_code = get_ordering(ordering, 'tag__')
        objects = TagFollower.objects.filter(filter_list).order_by(*ordering_code)

        if page == 0:
            objects = objects[:20]
        else:
            item_from = page * 20
            item_to = page * 20 + 20
            objects = objects[item_from:item_to]

        return objects
