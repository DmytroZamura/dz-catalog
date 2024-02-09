from django_elasticsearch_dsl import DocType, Index, fields
from .models import Post, PostCategory

posts = Index('posts')

@posts.doc_type
class PostDocument(DocType):
    id = fields.LongField(attr='id')

    post_categories = fields.IntegerField(attr='categories_indexing')

    country = fields.IntegerField(
        attr='country.id'
    )
    region = fields.IntegerField(
        attr='city.region.id'
    )
    city = fields.IntegerField(
        attr='city.id'
    )

    type = fields.IntegerField(
        attr='type.id'
    )

    job_type = fields.IntegerField(
        attr='post_job.job_type.id'
    )

    job_function = fields.IntegerField(
        attr='post_job.job_function.id'
    )

    seniority = fields.IntegerField(
        attr='post_job.seniority.id'
    )

    user = fields.StringField(
        attr='user.user_profile.name_all_languages'
    )
    company = fields.StringField(
        attr='company.name_all_languages'
    )
    product = fields.StringField(
        attr='product.name_all_languages'
    )
    community = fields.StringField(
        attr='community.name_all_languages'
    )
    category = fields.StringField(
        attr='category.name_all_languages'
    )

    is_open_community = fields.BooleanField(attr='is_open_community')


    class Meta:
        model = Post
        fields = [
            'comment',
            'city_name',
            'title',
            'post_title',
            'description',
            'published',
            'deleted',
            'update_date',
            'promotion',
            'promotion_grade'
        ]
        related_models = [PostCategory]

    def get_instances_from_related(self, related_instance):
        """If related_models is set, define how to retrieve the Car instance(s) from the related model.
        The related_models option should be used with caution because it can lead in the index
        to the updating of a lot of items.
        """
        if isinstance(related_instance, PostCategory):
            return related_instance.post





