import re
from django.db import IntegrityError
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Collection, ProductMedia
from django.contrib.auth.models import User
from rest_framework import serializers


from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    phone_number=serializers.CharField(max_length=15)
    class Meta:
        model = User
        fields = ('username', 'password','is_staff','is_superuser','email','phone_number')
        
    def validate_phone_number(self, value):
        try:
            pattern = r"^\+\d{1,3}[-\s]\d{9}$"
            if not re.match(pattern, value):
               raise serializers.ValidationError("Invalid phone number format")
            else:
                if User.objects.filter(phone_number=value).exclude(id=self.instance.id if self.instance else None).exists():
                    raise serializers.ValidationError("Phone number already exists")
                else:
                    return value
        except ValueError:
            raise serializers.ValidationError("Phone number must be a valid integer")
        
        



class ProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="id", read_only=True)  # Rename id → product_id
    user_id = serializers.IntegerField(source="user.id", read_only=True)  # Rename user → user_id

    class Meta:
        model = Product
        fields = ['product_id', 'user_id', 'name', 'description', 'price', 'stock']
        extra_kwargs = {
            'description': {'required': False},  # Make optional
            'price': {'required': False},
            'stock': {'required': False}
        }


class ProductMediaSerializer(serializers.ModelSerializer):
    """Serializer for handling Product Media uploads"""

    class Meta:
        model = ProductMedia
        fields = ['id', 'product', 'image_url']



class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'products']

    def create(self, validated_data):
        """Automatically assign the authenticated user to the collection"""
        request = self.context.get('request')
        if request and hasattr(request, "user"):
            validated_data['user'] = request.user  # Assign the user

        products_data = validated_data.pop('products', [])
        product_names = [product['name'] for product in products_data]

        # Check if a collection with the same name already exists for this user
        if Collection.objects.filter(name=validated_data['name'], user=request.user).exists():
            raise serializers.ValidationError({"name": "You already have a collection with this name."})

        # Get existing products that belong to the user
        existing_products = Product.objects.filter(name__in=product_names, user=request.user)

        # Find missing products
        existing_product_names = set(existing_products.values_list('name', flat=True))
        missing_products = set(product_names) - existing_product_names

        if missing_products:
            raise serializers.ValidationError({"products": f"These products do not exist: {', '.join(missing_products)}."})

        try:
            # Create collection and assign products
            collection = Collection.objects.create(**validated_data)
            collection.products.set(existing_products)
        except IntegrityError:
            raise serializers.ValidationError({"name": "You already have a collection with this name."})

        return collection    

    def update(self, instance, validated_data):
        """Handle updating collection and its products correctly"""
        request = self.context.get('request')
        if not request or not hasattr(request, "user"):
            raise serializers.ValidationError({"error": "Request context is missing."})

        # Extract product data
        products_data = validated_data.pop('products', [])

        # Prevent renaming to a duplicate name
        new_name = validated_data.get('name', instance.name)
        if new_name != instance.name and Collection.objects.filter(name=new_name, user=request.user).exists():
            raise serializers.ValidationError({"name": "You already have a collection with this name."})

        # Update collection fields
        instance.name = new_name
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Validate and update products
        product_names = [prod['name'] for prod in products_data]
        products = Product.objects.filter(name__in=product_names, user=request.user)

        # Find missing products
        existing_product_names = set(products.values_list('name', flat=True))
        missing_products = set(product_names) - existing_product_names

        if missing_products:
            raise serializers.ValidationError({"products": f"These products do not exist: {', '.join(missing_products)}."})

        instance.products.set(products)  # Assign new products to the collection
        return instance