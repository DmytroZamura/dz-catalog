from .models import Attribute, AttributeValue
from catalog.general.serializers import UnitTypeSerializer
from hvad.contrib.restframework.serializers import TranslatableModelSerializer


class AttributeSerializer(TranslatableModelSerializer):
    unit_type_details = UnitTypeSerializer(source='unit_type', required=False, read_only=True)
    class Meta:
        model = Attribute
        fields = ('id', 'type', 'multiple', 'unit_type', 'unit_type_details', 'name')



class AttributeValueSerializer(TranslatableModelSerializer):

    class Meta:
        model = AttributeValue
        fields = ('id', 'name')


