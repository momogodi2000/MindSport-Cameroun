import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()  # This line is crucial!

from backend.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(websocket_urlpatterns),
})