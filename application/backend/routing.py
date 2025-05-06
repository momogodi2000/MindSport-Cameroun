from django.urls import re_path
from .consumers import PrivateChatConsumer, ForumConsumer, NotificationConsumer
from .middleware import TokenAuthMiddlewareStack

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<conversation_id>\w+)/$', 
            TokenAuthMiddlewareStack(PrivateChatConsumer.as_asgi())),
    re_path(r'ws/forum/thread/(?P<thread_id>\w+)/$', 
            TokenAuthMiddlewareStack(ForumConsumer.as_asgi())),
    re_path(r'ws/forum/category/(?P<category_id>\w+)/$', 
            TokenAuthMiddlewareStack(ForumConsumer.as_asgi())),
    re_path(r'ws/forum/$', 
            TokenAuthMiddlewareStack(ForumConsumer.as_asgi())),
    re_path(r'ws/notifications/$', 
            TokenAuthMiddlewareStack(NotificationConsumer.as_asgi())),
]