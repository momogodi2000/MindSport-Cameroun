 # backend/decorators.py - Custom Decorators
    
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
    
def verified_user_required(function):
        """Decorator to check if user has a verified email/profile"""
        def wrapper(request, *args, **kwargs):
            if not request.user.is_verified:
                messages.warning(request, "You need to verify your account before accessing this feature.")
                return redirect('profile_verification')
            return function(request, *args, **kwargs)
        return wrapper
    
def athlete_required(function):
        """Decorator to check if user is an athlete"""
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'athlete_profile'):
                messages.warning(request, "This feature is only available for registered athletes.")
                return redirect(reverse('login'))
            return function(request, *args, **kwargs)
        return wrapper
    
def professional_required(function):
        """Decorator to check if user is a mental health professional"""
        def wrapper(request, *args, **kwargs):
            if not hasattr(request.user, 'professional_profile'):
                messages.warning(request, "This feature is only available for registered mental health professionals.")
                return redirect(reverse('login'))
            return function(request, *args, **kwargs)
        return wrapper
    
