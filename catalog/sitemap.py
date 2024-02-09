from django.contrib.sitemaps import Sitemap

from catalog.company.models import Company, CompanySEOData
from catalog.user_profile.models import UserProfile
from catalog.product.models import Product, ProductSEOData
from catalog.hashtag.models import TagQty
from catalog.post.models import PostSEOData, Article, Post

from django.utils import translation


class StaticSitemap(Sitemap):
    protocol = 'https'

    def items(self):
        return [
            '/feed/en',
            '/feed/ru',
            '/feed/uk',
            '/companies/en',
            '/companies/ru',
            '/companies/uk',
            '/products/en',
            '/products/ru',
            '/products/uk'
        ]

    def location(self, item):
        return item


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 1

    def items(self):
        return Article.objects.language('en').filter(allow_index=True, post__deleted=False, title__isnull=False,
                                                     text__isnull=False).order_by(
            'post__update_date')

    def lastmod(self, obj):
        return obj.post.update_date


class ArticleRuSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 1

    def items(self):
        return Article.objects.language('ru').filter(allow_index=True, post__deleted=False, title__isnull=False,
                                                     text__isnull=False).order_by(
            'post__update_date')

    def lastmod(self, obj):
        return obj.post.update_date


class ArticleUkSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 1

    def items(self):
        return Article.objects.language('uk').filter(allow_index=True, post__deleted=False, title__isnull=False,
                                                     text__isnull=False).order_by(
            'post__update_date')

    def lastmod(self, obj):
        return obj.post.update_date


class PostSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 1

    def items(self):
        return Post.objects.filter(allow_index=True, deleted=False, post_title__isnull=False,
                                   description__isnull=False, slug__isnull=False,
                                   comment__isnull=False, post_language__isnull=False).order_by(
            'update_date')

    def lastmod(self, obj):
        return obj.update_date


class CompanySitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Company.objects.language('en').filter(deleted=False).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class CompanyRuSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Company.objects.language('ru').filter(deleted=False).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class CompanyUkSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Company.objects.language('uk').filter(deleted=False).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class PeopleSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return UserProfile.objects.language('en').filter(deleted=False).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class PeopleRuSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return UserProfile.objects.language('ru').filter(deleted=False).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class PeopleUkSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return UserProfile.objects.language('uk').filter(deleted=False).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class ProductSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Product.objects.language('en').filter(deleted=False, published=True).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class ProductRuSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Product.objects.language('ru').filter(deleted=False, published=True).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class ProductUkSitemap(Sitemap):
    changefreq = "monthly"
    protocol = 'https'
    priority = 0.5

    def items(self):
        return Product.objects.language('uk').filter(deleted=False, published=True).order_by('update_date')

    def lastmod(self, obj):
        return obj.update_date


class ProductSEODataSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('en')
        return ProductSEOData.objects.all().order_by('create_date')


class ProductSEODataRuSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('ru')
        return ProductSEOData.objects.all().order_by('create_date')


class ProductSEODataUkSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('uk')
        return ProductSEOData.objects.all().order_by('create_date')


class CompanySEODataSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('en')
        return CompanySEOData.objects.all().order_by('create_date')


class CompanySEODataRuSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('ru')
        return CompanySEOData.objects.all().order_by('create_date')


class CompanySEODataUkSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('uk')
        return CompanySEOData.objects.all().order_by('create_date')


class PostSEODataSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('en')
        return PostSEOData.objects.filter(seniority__isnull=True).order_by('create_date')


class PostSEODataRuSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('ru')
        return PostSEOData.objects.filter(seniority__isnull=True).order_by('create_date')


class PostSEODataUkSitemap(Sitemap):
    changefreq = "daily"
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('uk')
        return PostSEOData.objects.filter(seniority__isnull=True).order_by('create_date')


class TagSitemap(Sitemap):
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('en')
        return TagQty.objects.all().order_by('tag_id')


class TagRuSitemap(Sitemap):
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('ru')
        return TagQty.objects.all().order_by('tag_id')


class TagUkSitemap(Sitemap):
    protocol = 'https'
    priority = 0.5

    def items(self):
        translation.activate('uk')
        return TagQty.objects.all().order_by('tag_id')


sitemaps = {
    'pages': StaticSitemap,
    'articles': ArticleSitemap,
    'articles-ru': ArticleRuSitemap,
    'articles-uk': ArticleUkSitemap,
    'offerings': PostSitemap,
    'companies': CompanySitemap,
    'companies-ru': CompanyRuSitemap,
    'companies-uk': CompanyUkSitemap,
    'companiesSEO': CompanySEODataSitemap,
    'companiesSEO-ru': CompanySEODataRuSitemap,
    'companiesSEO-uk': CompanySEODataUkSitemap,
    'people': PeopleSitemap,
    'people-ru': PeopleRuSitemap,
    'people-uk': PeopleUkSitemap,
    'products': ProductSitemap,
    'products-ru': ProductRuSitemap,
    'products-uk': ProductUkSitemap,
    'productsSEO': ProductSEODataSitemap,
    'productsSEO-ru': ProductSEODataRuSitemap,
    'productsSEO-uk': ProductSEODataUkSitemap,
    'posts': PostSEODataSitemap,
    'posts-ru': PostSEODataRuSitemap,
    'posts-uk': PostSEODataUkSitemap,
    'tags': TagSitemap,
    'tags-ru': TagRuSitemap,
    'tags-uk': TagUkSitemap,
}
