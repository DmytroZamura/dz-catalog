from django_elasticsearch_dsl import DocType, Index, fields
from .models import Community, CommunityCategory, CommunityEventsQty

communities = Index('communities')

@communities.doc_type
class CommunityDocument(DocType):

    country = fields.IntegerField(
        attr='country.id'
    )
    region = fields.IntegerField(
        attr='city.region.id'
    )
    city = fields.IntegerField(
        attr='city.id'
    )

    tags = fields.StringField(
        attr='tags_indexing'
    )
    categories = fields.IntegerField(attr='categories_indexing')

    name = fields.StringField(
        attr='name_all_languages'
    )

    description = fields.StringField(
        attr='description_all_languages'
    )



    members = fields.IntegerField(
        attr='eventsqty.members'
    )

    class Meta:
        model = Community
        fields = [
            'deleted',
            'update_date',

        ]

    related_models = [CommunityCategory, CommunityEventsQty]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, CommunityCategory):
            return related_instance.community





