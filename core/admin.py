from django.contrib import admin
from .models import User, Product, ProductMedia, Collection

# Register your models here.

admin.site.register(User)
admin.site.register(Product)
admin.site.register(ProductMedia)
admin.site.register(Collection)