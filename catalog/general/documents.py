from django_elasticsearch_dsl import DocType, Index, fields
from .models import City

cities = Index('cities')

@cities.doc_type
class CityDocument(DocType):

    country = fields.IntegerField(
        attr='country.id'
    )

    region= fields.IntegerField(
        attr='region.id'
    )

    location = fields.GeoPointField(attr='location_field_indexing')


    class Meta:
        model = City
        fields = [
            'default_name',
            'geoname_id',
            'slug',
            'population',
            'timezone'

        ]







