from rest_framework import serializers
from .models import TagFollower, TagQty, Tag
from catalog.user_profile.serializers import UserWithProfileSerializer


class TagQtySerializer(serializers.ModelSerializer):
    class Meta:
        model = TagQty
        fields = ('followers', )


class TagFollowerSerializer(serializers.ModelSerializer):
    user_data = UserWithProfileSerializer(source='user', required=False, read_only=True)

    class Meta:
        model = TagFollower
        fields = (
           'tag', 'user', 'user_data')





class TagSerializer(serializers.ModelSerializer):
    qty = TagQtySerializer(many=False, required=False, allow_null=True, read_only=True)
    follow_status = serializers.SerializerMethodField()

    def get_follow_status(self, obj):
        status = False

        if self.context:

            if self.context['request'].user.id:
                status = TagFollower.objects.filter(user=self.context['request'].user, tag=obj).exists()

        return status

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'qty', 'follow_status')


class FavoriteTagSerializer(serializers.ModelSerializer):
    tag_details = TagSerializer(source='tag', required=False, read_only=True)
    class Meta:
        model = TagFollower
        fields = (
           'tag', 'user', 'tag_details')