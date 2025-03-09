from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product

@registry.register_document
class ProductDocument(Document):
    user_id = fields.IntegerField(attr='user_id')
    
    class Index:
        name = 'products'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }

    class Django:
        model = Product
        fields = [
            'id',
            'name',
            'price',
            'stock',
            'slug'
        ]

    def get_queryset(self):
        return super().get_queryset().select_related('user')