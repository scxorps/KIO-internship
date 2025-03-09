from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Product
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_alert_email(product_id):
    try:
        product = Product.objects.get(id=product_id)
        subject = 'Stock Alert'
        message = f'The product "{product.name}" is running low on stock. Please restock it.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [product.user.email]
        send_mail(subject, message, from_email, recipient_list)
        return f'Alert email sent for product ID {product_id}'
    except Product.DoesNotExist:
        logger.error(f'Product with ID {product_id} does not exist')
    except Exception as e:
        logger.error(f'Error sending alert email for product ID {product_id}: {str(e)}')



@shared_task
def check_stock():
    products = Product.objects.filter(stock=0)
    for product in products:
        send_alert_email.delay(product.id)