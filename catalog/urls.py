from rest_framework.permissions import AllowAny
from django.contrib import admin

from django.conf.urls import include, url

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import generics

from django.conf import settings
from django.conf.urls.static import static

from catalog.sitemap import sitemaps
from django.contrib.sitemaps.views import sitemap, index
from django.views.decorators.cache import cache_page


# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


# ViewSets define the view behavior.
class UserdetailsView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    lookup_field = 'username'
    serializer_class = UserSerializer
    queryset = User.objects.all()


urlpatterns = [
    url(r'^sitemap\.xml$', cache_page(86400)(index), {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'^sitemap-(?P<section>.+)\.xml$', cache_page(86400)(sitemap), {'sitemaps': sitemaps}, name='sitemaps'),
    url(r'^admin/', include('smuggler.urls')),  # before admin url patterns!
    url(r'^admin/', admin.site.urls),
    # url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^api/user/(?P<username>.+)/$', UserdetailsView.as_view()),
    url(r'api/', include('catalog.general.urls')),
    url(r'api/', include('catalog.user_profile.urls')),
    url(r'api/', include('catalog.file.urls')),
    url(r'api/', include('catalog.post.urls')),
    url(r'api/', include('catalog.category.urls')),
    url(r'api/', include('catalog.product.urls')),
    url(r'api/', include('catalog.company.urls')),
    url(r'api/', include('catalog.community.urls')),
    url(r'api/', include('catalog.employment.urls')),
    url(r'api/', include('catalog.getstream.urls')),
    url(r'api/', include('catalog.messaging.urls')),
    url(r'api/', include('catalog.supply_request.urls')),
    url(r'api/', include('catalog.attribute.urls')),
    url(r'api/', include('catalog.mention.urls')),
    url(r'api/', include('catalog.hashtag.urls')),
    url(r'api/', include('catalog.payments.urls')),
    url(r'^health/?', include('health_check.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
