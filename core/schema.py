import graphene
from graphene_django.types import DjangoObjectType
from core.models import Product, User  # Import User model

# Define a GraphQL type for User
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email")  # Expose only id and email fields

# Define a GraphQL type for Product
class ProductType(DjangoObjectType):
    user = graphene.Field(UserType)  # Explicitly define user as a field

    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "user")  # Include user field

# Define Queries
class Query(graphene.ObjectType):
    all_products = graphene.List(ProductType)  # Query to fetch all products
    product = graphene.Field(ProductType, slug=graphene.String(required=True),username=graphene.String(required=True))

    
    def resolve_all_products(self, info):
        """Fetch all products from the database"""
        return Product.objects.select_related("user").all()  # Optimized query
    
    def resolve_product(self, info, slug,username):
        return Product.objects.select_related('user').get(slug=slug, user__username=username)

# Define the Schema
schema = graphene.Schema(query=Query)
