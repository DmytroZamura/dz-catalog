from django.core.management.base import BaseCommand
from catalog.category.models import Category, SuggestedCategory, CategoryAttribute, CategoryClassification
from catalog.post.models import PostSEOData, Post, PostCategory
from catalog.product.models import ProductSEOData, Product, ProductCategory
from catalog.company.models import CompanySEOData, CompanyCategory
from catalog.community.models import CommunityCategory
from catalog.user_profile.models import UserProfileCategory


def clear_seo_data():
    ProductSEOData.objects.all().delete()
    PostSEOData.objects.all().delete()
    CompanySEOData.objects.all().delete()


def clear_categories_related_objects():
    SuggestedCategory.objects.all().delete()
    PostCategory.objects.all().delete()
    ProductCategory.objects.all().delete()
    CompanyCategory.objects.all().delete()
    CommunityCategory.objects.all().delete()
    UserProfileCategory.objects.all().delete()
    CategoryAttribute.objects.all().delete()
    Post.objects.all().update(category=None)
    Product.objects.all().update(category=None)
    # Category.objects.all().update(users_exist=False, content_exists=False, posts_exist=False, companies_exist=False,
    #                               products_exist=False, communities_exist=False, parent=None)
    Category.objects.all().delete()
    # CategoryClassification.objects.all().delete()


def clear_categories_classification_positions():
    CategoryClassification.objects.all().update(level1_position=0, level2_position=0, level3_position=0,
                                                level4_position=0, level5_position=0, level6_position = 0,
                                                level1_code=None, level2_code=None, level3_code=None, level4_code=None,
                                                level5_code=None, level6_code=None)


class Command(BaseCommand):
    def handle(self, *args, **options):
        clear_seo_data()
        clear_categories_related_objects()
        clear_categories_classification_positions()
