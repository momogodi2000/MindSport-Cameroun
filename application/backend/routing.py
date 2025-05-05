from django.urls import re_path
from . import consumers
from .middleware import TokenAuthMiddlewareStack

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', 
            TokenAuthMiddlewareStack(consumers.PrivateChatConsumer.as_asgi())),
    re_path(r'ws/forum/thread/(?P<thread_id>\w+)/$', 
            TokenAuthMiddlewareStack(consumers.ForumConsumer.as_asgi())),
    re_path(r'ws/forum/category/(?P<category_id>\w+)/$', 
            TokenAuthMiddlewareStack(consumers.ForumConsumer.as_asgi())),
    re_path(r'ws/forum/$', 
            TokenAuthMiddlewareStack(consumers.ForumConsumer.as_asgi())),
    re_path(r'ws/notifications/$', 
            TokenAuthMiddlewareStack(consumers.NotificationConsumer.as_asgi())),
]