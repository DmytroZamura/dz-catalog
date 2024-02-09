from django_elasticsearch_dsl import DocType, Index, fields
from .models import Company, CompanyCategory, CompanyEventsQty

companies = Index('companies')


@companies.doc_type
class CompanyDocument(DocType):
    country = fields.IntegerField(
        attr='country.id'
    )
    region = fields.IntegerField(
        attr='city.region.id'
    )
    city = fields.IntegerField(
        attr='city.id'
    )

    company_industry = fields.IntegerField(
        attr='company_industry.id'
    )
    company_type = fields.IntegerField(
        attr='company_type.id'
    )
    company_size = fields.IntegerField(
        attr='company_size.id'
    )

    categories = fields.IntegerField(attr='categories_indexing')

    name = fields.StringField(
        attr='name_all_languages'
    )

    description = fields.StringField(
        attr='description_all_languages'
    )

    headline = fields.StringField(
        attr='headline_all_languages'
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

    followers = fields.IntegerField(
        attr='eventsqty.followers'
    )

    location = fields.GeoPointField(attr='location_field_indexing')

    class Meta:
        model = Company
        fields = [
            'address',
            'sales_email',
            'business_email',
            'website',
            'city_name',
            'address',
            'phone_number',
            'postal_code',
            'deleted',
            'update_date',

        ]

    related_models = [CompanyCategory, CompanyEventsQty]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, CompanyCategory):
            return related_instance.company
