from django.urls import path
from graphene_django.views import GraphQLView
from .views import ( CollectionDetailAPIView,
                    CollectionListCreateAPIView, ProductMediaAPIView,
                    ProductMediaDetailsAPIView, UserCreate,UserDetails,
                    ProductDetailAPIView, ProductListCreateAPIView)



urlpatterns = [
    path('signup/', UserCreate.as_view(), name='user-signup'),
    path('userdetails/', UserDetails.as_view(), name='user-details'),
    path('products/',ProductListCreateAPIView.as_view(),name='products'),
    path('products/<str:slug>/', ProductDetailAPIView.as_view(), name='product-details'),
    path('collections/', CollectionListCreateAPIView.as_view(), name='collections'),
    path('collections/<str:slug>/', CollectionDetailAPIView.as_view(), name='collection-details'),
    path('media/', ProductMediaAPIView.as_view(), name='create-product-media'),
    path('media/<int:pk>/', ProductMediaDetailsAPIView.as_view(), name='product-media-update-delete'),
    path("graphql/", GraphQLView.as_view(graphiql=True)),  # Enable GraphQL Playground
]