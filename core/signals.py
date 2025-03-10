# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver

from core.documents import ProductDocument
from .models import Product, ProductMedia

from core.models import ProductMedia

User = get_user_model()

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        print(f"🔥 Signal triggered for: {instance.email}")  # Debugging output
        subject = "Welcome to Our Platform!"
        message = f"Hello {instance.username},\n\nThank you for signing up on our platform!"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Email failed: {e}")

        


import boto3
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver
from core.models import ProductMedia

@receiver(post_delete, sender=ProductMedia)
def delete_image_on_s3(sender, instance, **kwargs):
    if instance.image_url:
        file_key = instance.image_url.name  # Ensure this is correct
        print(f"Attempting to delete: {file_key}")  # Debugging
        
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL
        )

        # Check if the file exists
        try:
            response = s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            print("File exists, proceeding with delete...")  
        except s3_client.exceptions.ClientError as e:
            print("File not found or incorrect key:", e)
            return  

        # Delete the file
        try:
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
            print(f"Deleted {file_key} successfully.")

            # Ensure the "hidden" version is also deleted
            hidden_key = file_key + ".b2_hidden"
            s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=hidden_key)
            print(f"Deleted hidden version: {hidden_key}")

        except Exception as e:
            print(f"Failed to delete {file_key}:", e)

        
        
@receiver(post_save, sender=Product)
def update_elasticsearch_on_save(sender, instance, **kwargs):
    """Sync product changes to Elasticsearch on save."""
    ProductDocument().update(instance)

# @receiver(post_delete, sender=Product)
# def delete_elasticsearch_on_delete(sender, instance, **kwargs):
#     """Remove product from Elasticsearch on delete."""
#     ProductDocument().delete(instance)