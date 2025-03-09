from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Product, Collection

User = get_user_model()

class ProductAPITestCase(APITestCase):
    
    def setUp(self):
        """Créer des utilisateurs et des objets pour les tests"""
        self.user = User.objects.create_user(username="testuser", password="testpass", email="test@example.com",phone_number="+213 672330269")
        self.other_user = User.objects.create_user(username="otheruser", password="testpass", email="testi@example.com",phone_number="+213 672330279")

        self.client.force_authenticate(user=self.user)
        
        self.product = Product.objects.create(name="Test Product", user=self.user, stock=10, price=10.99)
        self.collection = Collection.objects.create(name="Test Collection", user=self.user)

    # ✅ TESTS GET ✅
    def test_get_products(self):
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_detail(self):
        response = self.client.get(reverse("product-details", args=[self.product.slug]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_detail_not_found(self):
        response = self.client.get(reverse("product-details", args=["non-existent-slug"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_products_unauthenticated(self):
        """Un utilisateur non authentifié ne peut pas voir les produits"""
        self.client.logout()
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ✅ TESTS POST ✅
    def test_create_product(self):
        data = {"name": "New Product", "stock": 5, "price": 20.99}
        response = self.client.post(reverse("products"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_invalid(self):
        """Impossible de créer un produit sans nom"""
        data = {"stock": 5, "price": 20.99}  # Pas de "name"
        response = self.client.post(reverse("products"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ✅ TESTS PUT ✅
    def test_update_product(self):
        data = {"name": "Updated Product"}
        response = self.client.put(reverse("product-details", args=[self.product.slug]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Product")

    def test_update_product_not_found(self):
        data = {"name": "Updated Product"}
        response = self.client.put(reverse("product-details", args=["non-existent-slug"]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_other_user_product(self):
        """Un utilisateur ne peut pas modifier un produit qui ne lui appartient pas"""
        other_product = Product.objects.create(name="Other Product", user=self.other_user, stock=5, price=9.99)
        data = {"name": "Hacked Product"}
        response = self.client.put(reverse("product-details", args=[other_product.slug]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ✅ TESTS DELETE ✅
    def test_delete_product(self):
        response = self.client.delete(reverse("product-details", args=[self.product.slug]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_delete_product_not_found(self):
        response = self.client.delete(reverse("product-details", args=["non-existent-slug"]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_other_user_product(self):
        """Un utilisateur ne peut pas supprimer un produit qui ne lui appartient pas"""
        other_product = Product.objects.create(name="Other Product", user=self.other_user, stock=5, price=9.99)
        response = self.client.delete(reverse("product-details", args=[other_product.slug]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ✅ TESTS COLLECTIONS ✅
    def test_create_collection(self):
        data = {"name": "New Collection", "description": "this is a test", "products": [{"name": self.product.name}]}
        response = self.client.post(reverse("collections"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Collection.objects.count(), 2)

    def test_create_collection_invalid(self):
        """Impossible de créer une collection sans nom"""
        data = {"description": "No name collection"}
        response = self.client.post(reverse("collections"), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_collection_detail(self):
        response = self.client.get(reverse("collection-details", args=[self.collection.slug]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_collection(self):
        data = {"name": "Updated Collection"}
        response = self.client.put(reverse("collection-details", args=[self.collection.slug]), data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.collection.refresh_from_db()
        self.assertEqual(self.collection.name, "Updated Collection")

    def test_delete_collection(self):
        response = self.client.delete(reverse("collection-details", args=[self.collection.slug]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Collection.objects.filter(id=self.collection.id).exists())