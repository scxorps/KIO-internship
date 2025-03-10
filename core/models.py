from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import re


# Create your models here.
    
class User(AbstractUser):
    email = models.EmailField(unique=True, blank=False,max_length=255)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def clean(self):
        pattern=r"^\+\d{1,3}[-\s]?\d{9}$"
        if not re.match(pattern,self.phone_number):
            raise ValidationError("Invalid phone number format")
        if User.objects.filter(phone_number=self.phone_number).exclude(id=self.id).exists():
            raise ValidationError("Phone number already exists")
        
    def save(self, *args, **kwargs):
        # If the password is not already hashed, hash it
        self.clean()
        if self.pk is None or not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products",default=1)
    slug = models.SlugField(null=True,blank=True)
    
    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        super(Product,self).save(*args,**kwargs)
    
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'slug'], name='unique_product_per_user')
        ]
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    def __str__(self):
        return self.name
    

#product media 
class ProductMedia(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='media')
    image_url = models.ImageField(upload_to='products', null=False, blank=False)

    # def delete(self, *args, **kwargs):
    #     """Ensure file is deleted from storage when model instance is deleted"""
    #     storage = self.image_url.storage
    #     if storage.exists(self.image_url.name):
    #         storage.delete(self.image_url.name)  # ✅ Remove file from S3
    #     super().delete(*args, **kwargs)

    def __str__(self):
        return self.product.name 

class Collection(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    products = models.ManyToManyField('Product',blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="collections")
    slug = models.SlugField(null=True,blank=True)
    
    def save(self,*args,**kwargs):
        self.slug = slugify(self.name)
        super(Collection,self).save(*args,**kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['slug', 'user'], name='unique_collection_per_user')
        ]

    def __str__(self):
        return f"{self.name}" if self.user else self.name
