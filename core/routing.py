from django.urls import path
from core.consumers import NotificationConsumer  # Import your WebSocket consumer

websocket_urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
