from django.core.management.base import BaseCommand
from core.models import Product
from core.models import User

class Command(BaseCommand):
        
    def handle(self, *args, **kwargs):
        user=User.objects.get(id=1)
        sample_products = [
            {"name": "Produit A", "price": 10.99, "stock": 50},
            {"name": "Produit B", "price": 20.49, "stock": 30},
            {"name": "Produit C", "price": 5.99, "stock": 100},
        ]

        # Création en masse des produits
        products = [Product(user=user,**data) for data in sample_products]
        Product.objects.bulk_create(products)

        print(f'{len(products)} produits ajoutés avec succès !')