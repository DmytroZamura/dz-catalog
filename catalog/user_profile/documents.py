from django_elasticsearch_dsl import DocType, Index, fields
from .models import UserProfile, UserProfileCategory, UserProfileEventsQty
from catalog.employment.models import UserProfileEmployment

profiles = Index('profiles')


@profiles.doc_type
class ProfileDocument(DocType):
    name = fields.StringField(
        attr='name_all_languages'
    )

    description = fields.StringField(
        attr='description_all_languages'
    )

    headline = fields.StringField(
        attr='headline_all_languages'
    )

    employment = fields.StringField(
        attr='employment_all_languages'
    )

    tags = fields.StringField(
        attr='tags_indexing'
    )

    categories = fields.IntegerField(attr='categories_indexing')

    country = fields.IntegerField(
        attr='country.id'
    )
    region = fields.IntegerField(
        attr='city.region.id'
    )
    city = fields.IntegerField(
        attr='city.id'
    )

    is_active = fields.BooleanField(
        attr='user.is_active'
    )

    company_industry = fields.IntegerField(
        attr='company_industry_indexing'
    )
    company_type = fields.IntegerField(
        attr='company_type_indexing'
    )
    company_size = fields.IntegerField(
        attr='company_size_indexing'
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
        model = UserProfile
        fields = [
            'deleted',
            'update_date'

        ]

    related_models = [UserProfileCategory, UserProfileEmployment, UserProfileEventsQty]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Object instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, UserProfileCategory):
            return related_instance.profile

        if isinstance(related_instance, UserProfileEmployment):
            return related_instance.profile
