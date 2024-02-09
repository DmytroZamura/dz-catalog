from __future__ import unicode_literals
from .serializers import AttributeSerializer, AttributeValueSerializer
from .models import Attribute, AttributeValue
from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class AttributesSearch(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = AttributeSerializer

    @method_decorator(cache_page(60 * 20))
    def dispatch(self, *args, **kwargs):
        return super(AttributesSearch, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        name = self.kwargs['name']

        objects = Attribute.objects.language().filter(name__icontains=name).order_by('name')

        if not objects:
            objects = Attribute.objects.language('en').filter(name__icontains=name).order_by('name')

        return objects



class AttributeValues(generics.ListAPIView):
    permission_classes = (AllowAny,)

    serializer_class = AttributeValueSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def dispatch(self, *args, **kwargs):
        return super(AttributeValues, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        attribute = self.kwargs['attribute']

        objects = AttributeValue.objects.language().filter(attribute = attribute).order_by('name')

        return objects


