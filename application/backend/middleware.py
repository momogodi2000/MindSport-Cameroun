from django.contrib.auth import logout
from django.utils import timezone
from django.conf import settings
from django.shortcuts import redirect

from .forms import User

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip for non-authenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Check session last activity
        last_activity = request.session.get('last_activity')
        now = timezone.now().timestamp()

        if last_activity and now - last_activity > settings.SESSION_COOKIE_AGE:
            logout(request)
            return redirect('login')  # Redirect to login page after logout

        # Update last activity time
        request.session['last_activity'] = now

        return self.get_response(request)
    

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

@database_sync_to_async
def get_user(scope):
    close_old_connections()
    token = scope.get('query_string').decode().split('token=')[-1]
    
    if not token:
        return AnonymousUser()
    
    try:
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        return User.objects.get(id=user_id)
    except (InvalidToken, TokenError, User.DoesNotExist):
        return AnonymousUser()

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope['user'] = await get_user(scope)
        return await self.inner(scope, receive, send)

def TokenAuthMiddlewareStack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))
