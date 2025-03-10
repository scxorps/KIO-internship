from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.models import User
from django.shortcuts import get_object_or_404
from core.documents import ProductDocument
from core.models import Collection,Product,ProductMedia
from .serializers import CollectionSerializer,ProductMediaSerializer,ProductSerializer,UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from .tasks import check_stock



#signup user with classic method
class UserCreate(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#get user details
class UserDetails(APIView):
    serializer_class = UserSerializer
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request):
        user = request.user  # Get the currently authenticated user
        serializer = UserSerializer(user, data=request.data, partial=True)  # Allow partial updates
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        user = get_object_or_404(User, username=request.user.username)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
  
  
  

  

    
class ProductDetailAPIView(APIView):

    serializer_class = ProductSerializer
    
    def get_object(self, slug, user):
        """Retrieve the product only if the user created it"""
        return get_object_or_404(Product, slug=slug, user=user)


    def get(self, request, slug):
        product = self.get_object(slug, request.user)
        serializer = self.serializer_class(product)
        return Response(serializer.data)
    

    def put(self, request, slug):
        product = self.get_object(slug, request.user)       
        serializer = self.serializer_class(product, data=request.data, partial=True, context = {'user': request.user})
        if serializer.is_valid():
            try:
                prod = serializer.save() 
                # Check for low stock after saving
                if prod.stock == 0:
                    check_stock.delay()
                return Response(serializer.data)
            except IntegrityError:
                return Response({"error": "You already have a product with this name."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def delete(self, request, slug):
        product = self.get_object(slug, request.user)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)






class ProductListCreateAPIView(APIView):
    
    serializer_class = ProductSerializer
    
    def get(self, request):
        user = request.user
        qs = Product.objects.filter(user=user)

        # Print the search query
        search_query = request.GET.get('search', '').strip()
        print(f"🔎 Received search query: '{search_query}'")

        # Elasticsearch search
        if search_query:
            clean_query = search_query.rstrip('/').strip()
            print(f"🔍 Searching for: '{clean_query}' in Elasticsearch")

            search = ProductDocument.search().filter(
                'term', user_id=user.id
            ).query(
                'match',
                name=clean_query  # Allows partial matches like "moh"
            )

            try:
                response = search.execute()
                product_ids = [int(hit.meta.id) for hit in response]
                print(f"✅ Elasticsearch found IDs: {product_ids}")

                qs = qs.filter(id__in=product_ids)
            except Exception as e:
                print(f"❌ Elasticsearch error: {e}")
                return Response(
                    {"error": "Search service unavailable"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

        # Pagination
        paginator = PageNumberPagination()
        result_page = paginator.paginate_queryset(qs, request)
        serializer = self.serializer_class(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    

    def post(self,request):
        data=request.data
        if isinstance(data,list):
            serializer = self.serializer_class(data=data, context={'user': request.user}, many=True)
            if serializer.is_valid():
                products = [
                Product(user=request.user, **validated)
                for validated in serializer.validated_data
               ]
                created_products=Product.objects.bulk_create(products)
                return Response(self.serializer_class(created_products, many=True).data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.serializer_class(data=request.data, context={'user': request.user})
            if serializer.is_valid():
                product = serializer.save(user=request.user)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

  
    
    
class CollectionListCreateAPIView(APIView):
    serializer_class = CollectionSerializer
    def get(self, request):
        """Retrieve only collections created by the logged-in user"""
        collections = Collection.objects.filter(user=request.user)  # Only get user's collections
        serializer = self.serializer_class(collections, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a collection and assign it to the authenticated user"""
        serializer = self.serializer_class(data=request.data, context={'user': request.user,"request":request})  # Pass request context
        if serializer.is_valid():
            serializer.save(user=request.user)  # Automatically assign user
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    

class CollectionDetailAPIView(APIView):
    serializer_class = CollectionSerializer
    def get_object(self, slug, user):
        """Retrieve a collection that belongs to the authenticated user"""
        return get_object_or_404(Collection, slug=slug, user=user)  # Ensure only owner can access

    def get(self, request, slug):
        """Retrieve a specific collection that belongs to the authenticated user"""
        collection = self.get_object(slug, request.user)  # Only fetch if user owns it
        serializer = self.serializer_class(collection)  # Serialize the collection with products
        return Response(serializer.data)

    def put(self, request, slug):
        """Update a collection"""
        collection = self.get_object(slug, request.user)  # Ensure only owner can update
        serializer = self.serializer_class(collection, data=request.data, partial=True, context={'user': request.user,"request":request})
        if serializer.is_valid():
            serializer.save(user=request.user)  # ✅ Ensure user remains the same
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, slug):
        """Delete a collection"""
        collection = self.get_object(slug, request.user)  # Ensure only owner can delete
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    







class ProductMediaAPIView(APIView):
    """Handles retrieving, creating, updating, and deleting Product Media"""
    # parser_classes = [MultiPartParser, FormParser]  # Allows file uploads
    serializer_class = ProductMediaSerializer
    def get(self, request, pk=None):
        """Retrieve product media. If pk is provided, return a specific media file."""
        if pk:
            media = get_object_or_404(ProductMedia, pk=pk)
            if media.product.user != request.user:
                raise PermissionDenied("You do not have permission to view this media.")
            serializer = self.serializer_class(media)
        else:
            # Retrieve all media files for the authenticated user's products
            media = ProductMedia.objects.filter(product__user=request.user)
            serializer = self.serializer_class(media, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(request.data)
        """Upload a new media file for a product"""
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = get_object_or_404(Product, id=request.data.get('product'), user=request.user)
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
class ProductMediaDetailsAPIView(APIView):
    
    serializer_class = ProductMediaSerializer
    def get(self, request, pk):
        media = get_object_or_404(ProductMedia, pk=pk)
        serializer = self.serializer_class(media)
        return Response(serializer.data)
    
    def put(self, request, pk):
        media = get_object_or_404(ProductMedia, pk=pk)
        serializer = self.serializer_class(media, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        media = get_object_or_404(ProductMedia, pk=pk)
        
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)