from django_elasticsearch_dsl import DocType, Index, fields
from .models import Product, ProductCategory, ProductEventsQty

products = Index('products')

@products.doc_type
class ProductDocument(DocType):

    country = fields.IntegerField(
        attr='country_indexing'
    )
    region = fields.IntegerField(
        attr='region_indexing'
    )

    city = fields.IntegerField(
        attr='city_indexing'
    )

    categories = fields.IntegerField(attr='categories_indexing')

    city_name = fields.StringField(
        attr='city_name_indexing'
    )

    name = fields.StringField(
        attr='name_all_languages'
    )

    description = fields.StringField(
        attr='description_all_languages'
    )

    price_conditions = fields.StringField(
        attr='price_conditions_all_languages'
    )
    packaging_and_delivery = fields.StringField(
        attr='packaging_and_delivery_all_languages'
    )

    category = fields.StringField(
        attr='category.name_all_languages'
    )

    user = fields.StringField(
        attr='user.user_profile.name_all_languages'
    )
    company = fields.StringField(
        attr='company.name_all_languages'
    )

    product_group = fields.StringField(
        attr='product_group.name_all_languages'
    )

    country_origin = fields.StringField(
        attr='origin.name_all_languages'
    )

    tags = fields.StringField(
        attr='tags_indexing'
    )

    rating = fields.IntegerField(
        attr='eventsqty.rating'
    )

    related_reviews = fields.IntegerField(
        attr='eventsqty.related_reviews'
    )

    related_questions = fields.IntegerField(
        attr='eventsqty.related_questions'
    )


    price_usd_to = fields.FloatField(attr=None)

    location = fields.GeoPointField(attr='location_field_indexing')

    class Meta:
        model = Product
        fields = [
            'brand_name',
            'model_number',
            'published',
            'deleted',
            'discount',
            'update_date',

        ]

    related_models = [ProductCategory, ProductEventsQty]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, ProductCategory):
            return related_instance.product


