from functools import wraps
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import ContactForm, NewsletterForm, UserRegistrationForm
from .models import ContactMessage, NewsletterSubscriber, User
import uuid
import yagmail
import os
from datetime import datetime, timedelta, timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib import messages
from .forms import UserRegistrationForm, SocialSignupForm
from .models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Count, Q
from .models import User
import json
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import AppointmentRequest, SpecialistProfile, AppointmentReview, AppointmentNote
from .forms import AppointmentRequestForm, AppointmentResponseForm, AppointmentReviewForm, AppointmentNoteForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponseBadRequest
from django.db.models import Q, Avg
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.urls import reverse
import json
from datetime import datetime, timedelta
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Count, Avg, Q
from .models import *
from .scoring import ScoreCalculator
from .recommendation import RecommendationEngine

from .models import (
    ResourceCategory, WellnessResource, SavedResource, 
    ResourceRating, JournalEntry, JournalPrompt, JournalTemplate
)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
## admin mangement of forum
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView
from django.db.models import Count, Q
from django.utils import timezone

from .models import (
    Category, Thread, Comment, MentorshipProgram, MentorshipRelationship,
    AnonymousQuestion, SuccessStory, SupportGroup, SupportGroupSession,
    SupportGroupParticipant, SupportGroupAttendance
)

from .models import (
    Category, Thread, Comment, MentorshipProgram, MentorshipRelationship,
    AnonymousQuestion, SuccessStory, SupportGroup, SupportGroupSession,
    SupportGroupParticipant, SupportGroupAttendance
)
from backend.forms import (
    ThreadForm, CommentForm, AnonymousQuestionForm, SuccessStoryForm,
    MentorshipApplicationForm, SupportGroupRegistrationForm
)

from .decorators import verified_user_required, athlete_required, professional_required


# Get your User model
User = get_user_model()

from django.db import models

def home(request):
    newsletter_form = NewsletterForm()
    
    if request.method == 'POST':
        # Handle newsletter subscription
        newsletter_form = NewsletterForm(request.POST)
        if newsletter_form.is_valid():
            email = newsletter_form.cleaned_data['email']
            # Check if email already exists
            if not NewsletterSubscriber.objects.filter(email=email).exists():
                newsletter_form.save()
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            else:
                messages.info(request, 'This email is already subscribed to our newsletter.')
            return redirect('homepage')
    
    return render(request, 'LandingPage/HomePage.html', {
        'newsletter_form': newsletter_form
    })

def term(request):
    return render(request, 'LandingPage/term.html')


def contact_submit(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message. We will get back to you soon!')
            return redirect('homepage')
        else:
            # If form is invalid, we'll handle the error in the template
            pass
    return redirect('homepage')

def user_login(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request.user)
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember-me')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            
            # Set session expiry based on remember-me checkbox
            if not remember_me:
                request.session.set_expiry(3600)  # 1 hour in seconds
                request.session['last_activity'] = timezone.now().timestamp()
            
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect_to_dashboard(user)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'Authentication/Login.html')


def redirect_to_dashboard(user):
    """Helper function to redirect users to their appropriate dashboard"""
    if user.user_type == 'athlete':
        return redirect('athlete_dashboard')
    elif user.user_type == 'psychologist':
        return redirect('psychologist_dashboard')
    elif user.user_type == 'coach':
        return redirect('coach_dashboard')
    elif user.user_type == 'nutritionist':
        return redirect('nutritionist_dashboard')
    elif user.user_type == 'admin' or user.is_staff:
        return redirect('admin_dashboard')
    else:
        # Default fallback
        return redirect('homepage')

def register(request):
    if request.user.is_authenticated:
        # If user is already logged in, redirect to appropriate dashboard
        return redirect_to_dashboard(request.user)
        
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']  # Use email as username
            user.save()
            
            # Log the user in after registration - Fix: Specify the backend
            user.backend = 'django.contrib.auth.backends.ModelBackend'  # Specify the backend
            auth_login(request, user)
            
            messages.success(request, f'Welcome, {user.first_name}! Your registration was successful.')
            return redirect_to_dashboard(user)
    else:
        form = UserRegistrationForm(initial={'user_type': 'athlete'})  # Default to athlete
    
    return render(request, 'Authentication/Register.html', {'form': form})
class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        now = datetime.now().replace(tzinfo=self.expires_at.tzinfo)
        return not self.is_used and now < self.expires_at
    
    def __str__(self):
        return f"Reset token for {self.user.email}"

# Helper functions
def generate_verification_code():
    """Generate a 6-digit verification code"""
    import random
    return ''.join(random.choices('0123456789', k=6))

def send_reset_email(user_email, verification_code, reset_link):
    """Send password reset email using yagmail"""
    try:
        # Configure email settings (you should set these in your Django settings.py)
        email_user = settings.EMAIL_HOST_USER
        email_password = settings.EMAIL_HOST_PASSWORD
        
        # Email subject and body
        subject = "Password Reset Request - Mental Health Platform Cameroon"
        
        # HTML body with styling
        html_content = f"""
        <div style="font-family: 'Arial', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px; background-color: #f9f9f9;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #0284c7; margin-bottom: 10px;">Password Reset</h1>
                <p style="color: #555555; font-size: 16px;">Mental Health Platform Cameroon</p>
            </div>
            
            <div style="background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px;">
                <p style="margin-bottom: 15px; font-size: 15px; line-height: 1.5; color: #333333;">
                    We received a request to reset your password. To complete the process, please use the verification code below:
                </p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <div style="font-family: monospace; font-size: 24px; letter-spacing: 5px; background-color: #f0f9ff; padding: 15px; border-radius: 8px; display: inline-block; font-weight: bold; color: #0284c7; border: 1px dashed #90cdf4;">
                        {verification_code}
                    </div>
                </div>
                
                <p style="margin-bottom: 15px; font-size: 15px; line-height: 1.5; color: #333333;">
                    Alternatively, you can click the button below to reset your password directly:
                </p>
                
                <div style="text-align: center; margin: 25px 0;">
                    <a href="{reset_link}" style="background-color: #0284c7; color: white; text-decoration: none; padding: 12px 25px; border-radius: 5px; font-weight: bold; display: inline-block;">Reset Password</a>
                </div>
                
                <p style="margin-bottom: 15px; font-size: 14px; line-height: 1.5; color: #666666;">
                    If you didn't request a password reset, please ignore this email or contact support if you have concerns.
                </p>
                
                <p style="font-size: 14px; color: #777777;">
                    This code will expire in 5 minutes for security reasons.
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 20px; color: #888888; font-size: 13px;">
                <p>Mental Health Platform for Cameroonian Combat Athletes</p>
                <p>&copy; 2025 All rights reserved.</p>
            </div>
        </div>
        """
        
        # Initialize yagmail SMTP
        yag = yagmail.SMTP(email_user, email_password)
        
        # Send email
        yag.send(
            to=user_email,
            subject=subject,
            contents=html_content
        )
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# forgot pwd functions
def forgot_password(request):
    """Handle password reset request (Step 1)"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate verification code
            verification_code = generate_verification_code()
            
            # Set expiration time (5 minutes from now)
            expiry_time = datetime.now() + timedelta(minutes=5)
            
            # Create or update reset token
            reset_token, created = PasswordResetToken.objects.update_or_create(
                user=user,
                defaults={
                    'verification_code': verification_code,
                    'expires_at': expiry_time,
                    'is_used': False
                }
            )
            
            # Generate reset link
            reset_link = request.build_absolute_uri(
                f"{reverse('password_reset_verify')}?token={reset_token.token}&email={email}"
            )
            
            # Send email with reset instructions
            email_sent = send_reset_email(email, verification_code, reset_link)
            
            if email_sent:
                messages.success(request, "A password reset code has been sent to your email.")
                return redirect(f"{reverse('password_reset_verify')}?email={email}")
            else:
                messages.error(request, "Failed to send reset email. Please try again.")
        except ObjectDoesNotExist:
            # Don't reveal whether a user exists for security reasons
            messages.info(request, "If an account with this email exists, a reset link has been sent.")
            # Delay response to prevent timing attacks
            import time
            time.sleep(1)
        except Exception as e:
            messages.error(request, "An error occurred. Please try again later.")
            print(f"Password reset error: {e}")
    
    return render(request, 'Authentication/Forgot_password.html')

def password_reset_verify(request):
    """Handle verification code and password reset (Step 2 and 3)"""
    email = request.GET.get('email', '')
    token_uuid = request.GET.get('token', '')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        verification_code = request.POST.get('verificationCode')
        new_password = request.POST.get('newPassword')
        confirm_password = request.POST.get('confirmPassword')
        
        if not all([email, verification_code, new_password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, 'Authentication/Forgot_password.html', {'email': email})
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'Authentication/Forgot_password.html', {'email': email})
        
        try:
            user = User.objects.get(email=email)
            token = PasswordResetToken.objects.filter(
                user=user,
                verification_code=verification_code,
                is_used=False
            ).order_by('-created_at').first()
            
            if not token or not token.is_valid():
                messages.error(request, "Invalid or expired verification code.")
                return render(request, 'Authentication/Forgot_password.html', {'email': email})
            
            # Update password
            user.password = make_password(new_password)
            user.save()
            
            # Mark token as used
            token.is_used = True
            token.save()
            
            messages.success(request, "Your password has been successfully reset. You can now log in with your new password.")
            return redirect('login')
            
        except ObjectDoesNotExist:
            messages.error(request, "Invalid email or verification code.")
        except Exception as e:
            messages.error(request, "An error occurred. Please try again later.")
            print(f"Password reset verification error: {e}")
    
    return render(request, 'Authentication/Forgot_password.html', {'email': email})

def resend_verification_code(request):
    """API endpoint to resend verification code"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)
            
            # Generate new verification code
            verification_code = generate_verification_code()
            
            # Set expiration time (5 minutes from now)
            expiry_time = datetime.now() + timedelta(minutes=5)
            
            # Create or update reset token
            reset_token, created = PasswordResetToken.objects.update_or_create(
                user=user,
                defaults={
                    'verification_code': verification_code,
                    'expires_at': expiry_time,
                    'is_used': False
                }
            )
            
            # Generate reset link
            reset_link = request.build_absolute_uri(
                f"{reverse('password_reset_verify')}?token={reset_token.token}&email={email}"
            )
            
            # Send email with reset instructions
            email_sent = send_reset_email(email, verification_code, reset_link)
            
            if email_sent:
                return JsonResponse({'status': 'success', 'message': 'Verification code resent.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to send reset email.'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@login_required
def user_logout(request):
    # Get the user's name before logging out
    user_name = request.user.first_name
    
    # Log the user out
    logout(request)
    
    # Clear any session data
    request.session.flush()
    
    # Set a success message
    messages.success(request, f'Goodbye, {user_name}! You have been successfully logged out.')
    
    # Redirect to login page
    return redirect('login')

def social_signup_complete(request):
    if not request.user.is_authenticated or not request.user.social_provider:
        return redirect('register')
    
    if request.method == 'POST':
        form = SocialSignupForm(request.POST)
        if form.is_valid():
            user = request.user
            user.user_type = form.cleaned_data['user_type']
            user.sport = form.cleaned_data.get('sport')
            user.level = form.cleaned_data.get('level')
            user.qualifications = form.cleaned_data.get('qualifications')
            user.years_experience = form.cleaned_data.get('years_experience')
            user.terms_accepted = True
            user.save()
            
            messages.success(request, "Your account has been successfully created!")
            return redirect_to_dashboard(user)
    else:
        form = SocialSignupForm()
    
    return render(request, 'Authentication/social_signup_complete.html', {
        'form': form,
        'user': request.user
    })

def redirect_after_social_login(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.user_type:  # If user has already completed profile
        return redirect_to_dashboard(request.user)
    else:
        return redirect('social_signup_complete')

def redirect_to_dashboard(user):
    """Helper function to redirect users to their appropriate dashboard"""
    if user.user_type == 'athlete':
        return redirect('athlete_dashboard')
    elif user.user_type == 'psychologist':
        return redirect('psychologist_dashboard')
    elif user.user_type == 'coach':
        return redirect('coach_dashboard')
    elif user.user_type == 'nutritionist':
        return redirect('nutritionist_dashboard')
    elif user.user_type == 'admin' or user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('homepage')


# Placeholder dashboard views - create actual views based on your needs

@login_required
def psychologist_dashboard(request):
    return render(request, 'Dashboards/Psychologist/PsychologistPanel.html')

@login_required
def coach_dashboard(request):
    return render(request, 'Dashboards/Coach/CoachPanel.html')

@login_required
def nutritionist_dashboard(request):
    return render(request, 'Dashboards/Nutritionist/NutritionistPanel.html')

@login_required
def admin_dashboard(request):
    return render(request, 'Dashboards/Admin/AdminPanel.html')

# admin user management

def is_admin(user):
    return user.is_staff or user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_crud(request):
    # Get statistics for dashboard
    statistics = get_user_statistics()
    
    # Get all users for listing in the admin panel with filters
    users = User.objects.all().order_by('-date_joined')
    
    # Apply filters if provided
    user_type = request.GET.get('user_type')
    sport = request.GET.get('sport')
    level = request.GET.get('level')
    account_status = request.GET.get('account_status')
    payment_status = request.GET.get('payment_status')
    is_verified = request.GET.get('is_verified')
    search_query = request.GET.get('search', '')
    
    if user_type:
        users = users.filter(user_type=user_type)
    
    if sport:
        users = users.filter(sport=sport)
    
    if level:
        users = users.filter(level=level)
    
    if account_status:
        users = users.filter(account_status=account_status)
    
    if payment_status:
        users = users.filter(payment_status=payment_status)
    
    if is_verified:
        if is_verified == 'verified':
            users = users.filter(is_verified_professional=True)
        else:
            users = users.filter(is_verified_professional=False)
    
    if search_query:
        users = users.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(town__icontains=search_query) |
            Q(license_number__icontains=search_query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page', 1)
    users_page = paginator.get_page(page_number)
    
    # User growth data for chart
    user_growth = get_user_growth_data()
    
    # Get distinct values for filter dropdowns
    sport_choices = User.SPORT_CHOICES
    level_choices = User.LEVEL_CHOICES
    user_type_choices = User.USER_TYPE_CHOICES
    account_status_choices = User.ACCOUNT_STATUS_CHOICES
    payment_status_choices = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    )
    
    context = {
        'users': users_page,
        'statistics': statistics,
        'sport_choices': sport_choices,
        'level_choices': level_choices,
        'user_type_choices': user_type_choices,
        'account_status_choices': account_status_choices,
        'payment_status_choices': payment_status_choices,
        'user_growth_months': json.dumps(user_growth['months']),
        'user_growth_data': json.dumps(user_growth['data']),
        'selected_filters': {
            'user_type': user_type,
            'sport': sport,
            'level': level,
            'account_status': account_status,
            'payment_status': payment_status,
            'is_verified': is_verified,
            'search': search_query
        }
    }
    
    return render(request, 'Dashboards/Admin/User Management/admin_user.html', context)

def get_user_statistics():
    """Helper function to get user statistics"""
    statistics = {
        'total_users': User.objects.count(),
        'athlete_count': User.objects.filter(user_type='athlete').count(),
        'professional_count': User.objects.filter(user_type__in=['psychologist', 'coach', 'nutritionist']).count(),
        'psychologist_count': User.objects.filter(user_type='psychologist').count(),
        'coach_count': User.objects.filter(user_type='coach').count(),
        'nutritionist_count': User.objects.filter(user_type='nutritionist').count(),
        'admin_count': User.objects.filter(user_type='admin').count(),
        
        # Account status counts
        'pending_count': User.objects.filter(account_status='pending').count(),
        'active_count': User.objects.filter(account_status='active').count(),
        'blocked_count': User.objects.filter(account_status='blocked').count(),
        'suspended_count': User.objects.filter(account_status='suspended').count(),
        
        # Payment status counts
        'payment_pending_count': User.objects.filter(payment_status='pending').count(),
        'payment_paid_count': User.objects.filter(payment_status='paid').count(),
        'payment_failed_count': User.objects.filter(payment_status='failed').count(),
        'payment_expired_count': User.objects.filter(payment_status='expired').count(),
        
        # Verification status
        'verified_professionals': User.objects.filter(is_verified_professional=True).count(),
        'unverified_professionals': User.objects.filter(
            user_type__in=['psychologist', 'coach', 'nutritionist'],
            is_verified_professional=False
        ).count(),
        
        # Sport counts
        'boxing_count': User.objects.filter(sport='boxing').count(),
        'wrestling_count': User.objects.filter(sport='wrestling').count(),
        'judo_count': User.objects.filter(sport='judo').count(),
        'karate_count': User.objects.filter(sport='karate').count(),
        'taekwondo_count': User.objects.filter(sport='taekwondo').count(),
        'mma_count': User.objects.filter(sport='mma').count(),
        'other_sport_count': User.objects.filter(sport='other').count(),
        
        # Level counts
        'amateur_count': User.objects.filter(level='amateur').count(),
        'semipro_count': User.objects.filter(level='semi-pro').count(),
        'professional_count': User.objects.filter(level='professional').count(),
        'elite_count': User.objects.filter(level='elite').count(),
        
        # New users statistics
        'new_users_30_days': User.objects.filter(date_joined__gte=datetime.now() - timedelta(days=30)).count(),
        'new_users_7_days': User.objects.filter(date_joined__gte=datetime.now() - timedelta(days=7)).count(),
        'new_users_today': User.objects.filter(date_joined__date=datetime.now().date()).count(),
    }
    
    return statistics

@login_required
@user_passes_test(is_admin)
def admin_get_user(request, user_id):
    """View a single user's details"""
    user = get_object_or_404(User, id=user_id)
    
    # Calculate subscription status
    subscription_active = user.is_subscription_active()
    
    # Get payment history if we had a Payment model
    # payments = Payment.objects.filter(user=user).order_by('-payment_date')
    
    context = {
        'user': user,
        'subscription_active': subscription_active,
        'account_status_choices': User.ACCOUNT_STATUS_CHOICES,
        # 'payments': payments
    }
    
    return render(request, 'Dashboards/Admin/User Management/admin_user_detail.html', context)

@login_required
@user_passes_test(is_admin)
def admin_create_user(request):
    """Create a new user"""
    if request.method == 'POST':
        try:
            # Process form data
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            user_type = request.POST.get('user_type')
            password = request.POST.get('password', User.objects.make_random_password())
            
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
                return redirect('admin_create_user')
            
            # Create user with basic fields
            new_user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,
                terms_accepted=True
            )
            
            # Update fields based on user type
            new_user.sport = request.POST.get('sport')
            new_user.level = request.POST.get('level')
            new_user.town = request.POST.get('town')
            new_user.quartier = request.POST.get('quartier')
            new_user.mobile_number = request.POST.get('mobile_number')
            new_user.account_status = request.POST.get('account_status', 'pending')
            
            # Professional-specific fields
            if user_type in ['psychologist', 'coach', 'nutritionist']:
                new_user.qualifications = request.POST.get('qualifications')
                new_user.years_experience = request.POST.get('years_experience')
                new_user.license_number = request.POST.get('license_number')
                new_user.is_verified_professional = request.POST.get('is_verified_professional') == 'on'
                
                if new_user.is_verified_professional:
                    new_user.date_verified = timezone.now()
                    
                # Handle file uploads if present
                if 'certification_document' in request.FILES:
                    new_user.certification_document = request.FILES['certification_document']
                
                if 'cv_document' in request.FILES:
                    new_user.cv_document = request.FILES['cv_document']
                
                if 'additional_documents' in request.FILES:
                    new_user.additional_documents = request.FILES['additional_documents']
                
                new_user.verification_notes = request.POST.get('verification_notes')
            
            # Handle profile image if present
            if 'profile_image' in request.FILES:
                new_user.profile_image = request.FILES['profile_image']
            
            # Payment related fields
            payment_status = request.POST.get('payment_status')
            if payment_status:
                new_user.payment_status = payment_status
                
                if payment_status == 'paid':
                    new_user.last_payment_date = timezone.now()
                    new_user.next_payment_due = timezone.now() + timezone.timedelta(days=30)
            
            new_user.save()
            
            messages.success(request, f'User {first_name} {last_name} created successfully!')
            return redirect('admin_get_users')
            
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return redirect('admin_create_user')
    
    # GET request - show create form with all choices from model
    context = {
        'user_type_choices': User.USER_TYPE_CHOICES,
        'sport_choices': User.SPORT_CHOICES,
        'level_choices': User.LEVEL_CHOICES,
        'account_status_choices': User.ACCOUNT_STATUS_CHOICES,
        'payment_status_choices': (
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('expired', 'Expired'),
        )
    }
    
    return render(request, 'Dashboards/Admin/User Management/admin_create_user.html', context)

@login_required
@user_passes_test(is_admin)
def admin_update_user(request, user_id):
    """Update an existing user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        try:
            # Process form data for basic fields
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.user_type = request.POST.get('user_type', user.user_type)
            
            # Check if email changed and is unique
            new_email = request.POST.get('email')
            if new_email != user.email and User.objects.filter(email=new_email).exists():
                messages.error(request, 'Email already in use by another account')
                return redirect('admin_update_user', user_id=user_id)
            
            user.email = new_email
            user.username = new_email  # Keep username and email in sync
            
            # Update common fields
            user.sport = request.POST.get('sport', user.sport)
            user.level = request.POST.get('level', user.level)
            user.town = request.POST.get('town', user.town)
            user.quartier = request.POST.get('quartier', user.quartier)
            user.mobile_number = request.POST.get('mobile_number', user.mobile_number)
            user.account_status = request.POST.get('account_status', user.account_status)
            
            # Professional-specific fields
            if user.user_type in ['psychologist', 'coach', 'nutritionist']:
                user.qualifications = request.POST.get('qualifications', user.qualifications)
                user.years_experience = request.POST.get('years_experience', user.years_experience)
                user.license_number = request.POST.get('license_number', user.license_number)
                
                was_verified = user.is_verified_professional
                user.is_verified_professional = request.POST.get('is_verified_professional') == 'on'
                
                # Set verification date if newly verified
                if not was_verified and user.is_verified_professional:
                    user.date_verified = timezone.now()
                
                # Handle file uploads if present
                if 'certification_document' in request.FILES:
                    user.certification_document = request.FILES['certification_document']
                
                if 'cv_document' in request.FILES:
                    user.cv_document = request.FILES['cv_document']
                
                if 'additional_documents' in request.FILES:
                    user.additional_documents = request.FILES['additional_documents']
                
                user.verification_notes = request.POST.get('verification_notes', user.verification_notes)
            
            # Handle profile image if present
            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
            
            # Payment related fields
            payment_status = request.POST.get('payment_status')
            if payment_status and payment_status != user.payment_status:
                user.payment_status = payment_status
                
                if payment_status == 'paid' and (not user.last_payment_date or user.payment_status != 'paid'):
                    user.last_payment_date = timezone.now()
                    user.next_payment_due = timezone.now() + timezone.timedelta(days=30)
            
            # Manually set membership fee if provided
            if request.POST.get('membership_fee'):
                user.membership_fee = request.POST.get('membership_fee')
            
            # Handle password update if provided
            password = request.POST.get('password')
            if password:
                user.set_password(password)
            
            user.save()
            messages.success(request, f'User {user.get_full_name()} updated successfully!')
            return redirect('admin_get_users')
            
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
            return redirect('admin_update_user', user_id=user_id)
    
    # GET request - show update form with choices from model
    context = {
        'user': user,
        'user_type_choices': User.USER_TYPE_CHOICES,
        'sport_choices': User.SPORT_CHOICES,
        'level_choices': User.LEVEL_CHOICES,
        'account_status_choices': User.ACCOUNT_STATUS_CHOICES,
        'payment_status_choices': (
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('expired', 'Expired'),
        )
    }
    
    return render(request, 'Dashboards/Admin/User Management/admin_update_user.html', context)

@login_required
@user_passes_test(is_admin)
def admin_verify_professional(request, user_id):
    """Verify a professional user"""
    user = get_object_or_404(User, id=user_id)
    
    if user.user_type not in ['psychologist', 'coach', 'nutritionist']:
        messages.error(request, f'User {user.get_full_name()} is not a professional account')
        return redirect('admin_get_user', user_id=user_id)
    
    user.is_verified_professional = True
    user.date_verified = timezone.now()
    user.account_status = 'active'
    user.save()
    
    # Send verification email to user
    # send_verification_email(user)
    
    messages.success(request, f'Professional {user.get_full_name()} has been verified successfully')
    return redirect('admin_get_user', user_id=user_id)

@login_required
@user_passes_test(is_admin)
def admin_update_account_status(request, user_id):
    """Update account status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        new_status = request.POST.get('account_status')
        
        if new_status in dict(User.ACCOUNT_STATUS_CHOICES):
            user.account_status = new_status
            user.save()
            messages.success(request, f'Account status for {user.get_full_name()} updated to {new_status}')
        else:
            messages.error(request, 'Invalid account status')
        
        return redirect('admin_get_user', user_id=user_id)
    
    return redirect('admin_get_users')

@login_required
@user_passes_test(is_admin)
def admin_get_statistics(request):
    """View detailed statistics"""
    statistics = get_user_statistics()
    
    # Get more detailed statistics
    # Get new users by month for the last 6 months
    six_months_ago = datetime.now() - timedelta(days=180)
    
    monthly_signups = (
        User.objects.filter(date_joined__gte=six_months_ago)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Get athletes by level
    athletes_by_level = User.objects.filter(
        user_type='athlete'
    ).values('level').annotate(count=Count('id'))
    
    # Get professionals by verification status
    professionals_by_verification = User.objects.filter(
        user_type__in=['psychologist', 'coach', 'nutritionist']
    ).values('user_type', 'is_verified_professional').annotate(count=Count('id'))
    
    # Get users by payment status
    users_by_payment = User.objects.values('payment_status').annotate(count=Count('id'))
    
    # Get users by account status
    users_by_account_status = User.objects.values('account_status').annotate(count=Count('id'))
    
    # Get users by town
    users_by_town = User.objects.exclude(town__isnull=True).exclude(town='').values('town').annotate(count=Count('id')).order_by('-count')[:10]
    
    user_growth = get_user_growth_data()
    
    context = {
        'statistics': statistics,
        'monthly_signups': list(monthly_signups),
        'athletes_by_level': list(athletes_by_level),
        'professionals_by_verification': list(professionals_by_verification),
        'users_by_payment': list(users_by_payment),
        'users_by_account_status': list(users_by_account_status),
        'users_by_town': list(users_by_town),
        'user_growth_months': json.dumps(user_growth['months']),
        'user_growth_data': json.dumps(user_growth['data'])
    }
    
    return render(request, 'Dashboards/Admin/User Management/admin_statistics.html', context)

@login_required
@user_passes_test(is_admin)
def admin_export_users(request):
    """Export users to CSV/Excel"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    # Header row
    writer.writerow([
        'ID', 'Email', 'First Name', 'Last Name', 'User Type', 
        'Date Joined', 'Sport', 'Level', 'Town', 'Quartier',
        'Mobile Number', 'Account Status', 'Payment Status',
        'Is Verified Professional', 'Qualifications', 'Years Experience',
        'License Number', 'Last Payment Date', 'Next Payment Due',
        'Membership Fee'
    ])
    
    # Apply filters from request if any
    users = User.objects.all().order_by('-date_joined')
    
    # Get filter parameters
    user_type = request.GET.get('user_type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Add additional filters as needed
    # [...]
    
    # Export data
    for user in users:
        writer.writerow([
            user.id, user.email, user.first_name, user.last_name,
            user.get_user_type_display(), user.date_joined, 
            user.get_sport_display() if user.sport else '',
            user.get_level_display() if user.level else '',
            user.town or '', user.quartier or '',
            user.mobile_number or '', user.get_account_status_display(),
            user.payment_status,
            'Yes' if user.is_verified_professional else 'No',
            user.qualifications or '', user.years_experience or '',
            user.license_number or '',
            user.last_payment_date or '', user.next_payment_due or '',
            user.membership_fee
        ])
    
    return response

@login_required
@user_passes_test(is_admin)
def admin_delete_user(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_name = user.get_full_name()
        user.delete()
        messages.success(request, f'User {user_name} has been deleted successfully')
        return redirect('admin_get_users')
    
    # If GET request, show confirmation page
    return render(request, 'Dashboards/Admin/User Management/admin_user.html', {'user': user})

def get_user_growth_data():
    """Helper function to get user growth data for charts"""
    from django.db.models.functions import TruncMonth
    from django.db.models import Count
    from datetime import datetime, timedelta
    
    # Get data for the last 12 months
    twelve_months_ago = datetime.now() - timedelta(days=365)
    
    # Get monthly signups
    monthly_data = (
        User.objects
        .filter(date_joined__gte=twelve_months_ago)
        .annotate(month=TruncMonth('date_joined'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    
    # Prepare data for chart
    months = []
    counts = []
    
    for entry in monthly_data:
        months.append(entry['month'].strftime('%b %Y'))
        counts.append(entry['count'])
    
    return {
        'months': months,
        'data': counts
    }

#admin contact management and update this part for production
@login_required
def contact_management(request):
    # Handle contact messages
    if request.method == 'POST':
        # Reply to a contact message
        if 'reply_message' in request.POST:
            message_id = request.POST.get('message_id')
            reply_content = request.POST.get('reply_content')
            
            try:
                message = ContactMessage.objects.get(id=message_id)
                
                # Send email reply using yagmail
                import yagmail
                
                # Configure your email credentials - should be in settings.py in production
                sender_email = "yvangodimomo@gmail.com"
                sender_password = "pzls apph esje cgdl"  # Use environment variables in production
                
                # Initialize yagmail
                yag = yagmail.SMTP(sender_email, sender_password)
                
                # Send the email
                yag.send(
                    to=message.email,
                    subject=f"Re: {message.subject}",
                    contents=reply_content
                )
                
                messages.success(request, f"Reply sent to {message.email}")
                
            except ContactMessage.DoesNotExist:
                messages.error(request, "Message not found")
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
                
            return redirect('contact_management')
            
        # Delete a contact message
        elif 'delete_message' in request.POST:
            message_id = request.POST.get('message_id')
            
            try:
                message = ContactMessage.objects.get(id=message_id)
                message.delete()
                messages.success(request, "Message deleted successfully")
            except ContactMessage.DoesNotExist:
                messages.error(request, "Message not found")
                
            return redirect('contact_management')
            
        # Add a newsletter subscriber
        elif 'add_subscriber' in request.POST:
            email = request.POST.get('subscriber_email')
            is_active = request.POST.get('subscriber_active') == 'on'
            
            try:
                subscriber, created = NewsletterSubscriber.objects.get_or_create(
                    email=email,
                    defaults={'is_active': is_active}
                )
                
                if not created:
                    subscriber.is_active = is_active
                    subscriber.save()
                    messages.success(request, f"Subscriber {email} updated")
                else:
                    messages.success(request, f"Subscriber {email} added successfully")
                    
            except Exception as e:
                messages.error(request, f"Failed to add subscriber: {str(e)}")
                
            return redirect('contact_management')
            
        # Delete a subscriber
        elif 'delete_subscriber' in request.POST:
            subscriber_id = request.POST.get('subscriber_id')
            
            try:
                subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
                subscriber.delete()
                messages.success(request, "Subscriber removed successfully")
            except NewsletterSubscriber.DoesNotExist:
                messages.error(request, "Subscriber not found")
                
            return redirect('contact_management')
            
        # Toggle subscriber active status
        elif 'toggle_subscriber' in request.POST:
            subscriber_id = request.POST.get('subscriber_id')
            
            try:
                subscriber = NewsletterSubscriber.objects.get(id=subscriber_id)
                subscriber.is_active = not subscriber.is_active
                subscriber.save()
                status = "activated" if subscriber.is_active else "deactivated"
                messages.success(request, f"Subscriber {subscriber.email} {status}")
            except NewsletterSubscriber.DoesNotExist:
                messages.error(request, "Subscriber not found")
                
            return redirect('contact_management')
            
        # Send mass email to subscribers
        elif 'send_newsletter' in request.POST:
            subject = request.POST.get('email_subject')
            content = request.POST.get('email_content')
            
            # Get active subscribers
            subscribers = NewsletterSubscriber.objects.filter(is_active=True)
            
            if not subscribers.exists():
                messages.warning(request, "No active subscribers to send emails to")
                return redirect('contact_management')
                
            try:
                # Send email using yagmail
                import yagmail
                
                # Configure email credentials - should be in settings.py in production
                sender_email = "yvangodimomo@gmail.com"
                sender_password = "pzls apph esje cgdl"  # Use environment variables in production
                
                # Initialize yagmail
                yag = yagmail.SMTP(sender_email, sender_password)
                
                # Handle file attachments
                attachments = []
                if request.FILES.getlist('email_attachments'):
                    for file in request.FILES.getlist('email_attachments'):
                        # Save the file temporarily
                        import tempfile
                        import os
                        
                        temp = tempfile.NamedTemporaryFile(delete=False)
                        temp.write(file.read())
                        temp.close()
                        
                        attachments.append(temp.name)
                
                # Send to all active subscribers
                for subscriber in subscribers:
                    yag.send(
                        to=subscriber.email,
                        subject=subject,
                        contents=content,
                        attachments=attachments
                    )
                
                # Clean up temporary files
                for attachment in attachments:
                    os.unlink(attachment)
                    
                messages.success(request, f"Newsletter sent to {subscribers.count()} subscribers")
                
            except Exception as e:
                messages.error(request, f"Failed to send newsletter: {str(e)}")
                
            return redirect('contact_management')
            
    # Export contact emails
    elif 'export_contacts' in request.GET:
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contact_emails.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Name', 'Email', 'Subject', 'Date'])
        
        contacts = ContactMessage.objects.all().order_by('-created_at')
        for contact in contacts:
            writer.writerow([
                contact.name, 
                contact.email, 
                contact.subject, 
                contact.created_at.strftime('%Y-%m-%d %H:%M')
            ])
            
        return response
        
    # Export subscriber emails
    elif 'export_subscribers' in request.GET:
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="newsletter_subscribers.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Status', 'Subscribed Date'])
        
        subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
        for subscriber in subscribers:
            writer.writerow([
                subscriber.email, 
                'Active' if subscriber.is_active else 'Inactive', 
                subscriber.subscribed_at.strftime('%Y-%m-%d %H:%M')
            ])
            
        return response
    
  # Get all contact messages and subscribers for template
    contact_messages = ContactMessage.objects.all().order_by('-created_at')
    subscribers = NewsletterSubscriber.objects.all().order_by('-subscribed_at')
    active_subscribers_count = NewsletterSubscriber.objects.filter(is_active=True).count()
    
    return render(request, 'Dashboards/Admin/management_contact/admin_management_contact.html', {
        'contact_messages': contact_messages,
        'subscribers': subscribers,
        'active_subscribers_count': active_subscribers_count,  # Pass the count to the template
    })



#Athlect panel

@login_required
def appointments(request):
    """Main appointments view for athletes"""
    # Ensure user is an athlete
    if request.user.user_type != 'athlete':
        messages.error(request, "This page is only accessible to athletes")
        return redirect('manage_appointment_requests')
    
    # Get athlete's appointments
    upcoming_appointments = AppointmentRequest.objects.filter(
        athlete=request.user,
        date__gte=timezone.now().date(),
        status__in=['pending', 'accepted']
    ).order_by('date', 'time')
    
    past_appointments = AppointmentRequest.objects.filter(
        athlete=request.user,
        status='completed'
    ).order_by('-date', '-time')
    
    canceled_appointments = AppointmentRequest.objects.filter(
        athlete=request.user,
        status__in=['rejected', 'canceled']
    ).order_by('-date', '-time')
    
    # Calculate stats
    upcoming_count = upcoming_appointments.count()
    completed_count = AppointmentRequest.objects.filter(
        athlete=request.user,
        status='completed'
    ).count()
    
    # Calculate total hours
    total_minutes = sum(
        appointment.duration for appointment in 
        AppointmentRequest.objects.filter(athlete=request.user, status='completed')
    )
    total_hours = round(total_minutes / 60, 1)
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'canceled_appointments': canceled_appointments,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'total_hours': total_hours,
    }
    
    return render(request, 'Dashboards/Athlete/Appointments/Appointments.html', context)

@login_required
def specialist_list(request):
    """View to list all specialists for booking"""
    # Get the selected specialist type
    specialist_type = request.GET.get('type', None)
    
    # Base query for all verified professionals
    specialists_query = User.objects.filter(
        is_verified_professional=True,
        account_status='active'
    )
    
    # Filter by specialist type if provided
    if specialist_type and specialist_type in ['psychologist', 'coach', 'nutritionist']:
        specialists_query = specialists_query.filter(user_type=specialist_type)
    else:
        specialists_query = specialists_query.filter(
            user_type__in=['psychologist', 'coach', 'nutritionist']
        )
    
    # Search by name if provided
    search_term = request.GET.get('search', '')
    if search_term:
        specialists_query = specialists_query.filter(
            Q(first_name__icontains=search_term) | 
            Q(last_name__icontains=search_term) |
            Q(specialist_profile__expertise_areas__icontains=search_term)
        )
    
    # Paginate results
    paginator = Paginator(specialists_query, 12)  # 12 specialists per page
    page_number = request.GET.get('page', 1)
    specialists = paginator.get_page(page_number)
    
    context = {
        'specialists': specialists,
        'specialist_type': specialist_type,
        'search_term': search_term,
    }
    
    return render(request, 'Dashboards/Athlete/Appointments/specialist_list.html', context)

@login_required
def specialist_detail(request, specialist_id):
    """View specialist details and availability"""
    specialist = get_object_or_404(User, id=specialist_id, is_verified_professional=True)
    
    # Check if the specialist has a profile, create one if not
    try:
        profile = specialist.specialist_profile
    except SpecialistProfile.DoesNotExist:
        profile = SpecialistProfile.objects.create(user=specialist)
    
    # Get available time slots
    available_dates = get_available_slots(specialist)
    
    context = {
        'specialist': specialist,
        'profile': profile,
        'available_dates': available_dates,
    }
    
    return render(request, 'Dashboards/Athlete/Appointments/specialist_detail.html', context)

@login_required
def create_appointment(request):
    """Create a new appointment request"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.athlete = request.user
            appointment.save()
            
            # Send notification to specialist (could be implemented with Django signals)
            
            messages.success(request, "Appointment request sent successfully!")
            return redirect('appointments')
    else:
        # Get specialist ID from URL if provided
        specialist_id = request.GET.get('specialist', None)
        initial_data = {}
        selected_specialist = None
        
        if specialist_id:
            try:
                selected_specialist = User.objects.get(id=specialist_id)
                initial_data['specialist'] = selected_specialist
            except User.DoesNotExist:
                pass
                
        form = AppointmentRequestForm(initial=initial_data)
    
    # Query available specialists for the dropdown
    available_specialists = User.objects.filter(
        is_verified_professional=True,
        account_status='active',
        user_type__in=['psychologist', 'coach', 'nutritionist']
    )
    
    context = {
        'form': form,
        'available_specialists': available_specialists,
        'selected_specialist': selected_specialist,
        'today': timezone.now(),
    }
    
    return render(request, 'Dashboards/Athlete/Appointments/create_appointment.html', context)

@login_required
def manage_appointment_requests(request):
    """View for specialists to manage appointment requests"""
    # Ensure user is a specialist
    if request.user.user_type not in ['psychologist', 'coach', 'nutritionist']:
        messages.error(request, "This page is only accessible to healthcare providers")
        return redirect('dashboard')
    
    # Get appointment requests for this specialist
    pending_requests = AppointmentRequest.objects.filter(
        specialist=request.user,
        status='pending'
    ).order_by('date', 'time')
    
    upcoming_appointments = AppointmentRequest.objects.filter(
        specialist=request.user,
        status='accepted',
        date__gte=timezone.now().date()
    ).order_by('date', 'time')
    
    past_appointments = AppointmentRequest.objects.filter(
        specialist=request.user,
        status='completed'
    ).order_by('-date', '-time')
    
    context = {
        'pending_requests': pending_requests,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
    }
    
    return render(request, 'Dashboards/Common/appointment_requests.html', context)

@login_required
def respond_to_appointment(request, appointment_id):
    """Accept or reject an appointment request"""
    appointment = get_object_or_404(
        AppointmentRequest, 
        id=appointment_id,
        specialist=request.user,
        status='pending'
    )
    
    if request.method == 'POST':
        form = AppointmentResponseForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            
            # Set status based on form submission
            action = request.POST.get('action')
            if action == 'accept':
                appointment.status = 'accepted'
                # Generate Jitsi room details
                appointment.generate_jitsi_room_details()
            elif action == 'reject':
                appointment.status = 'rejected'
            
            appointment.save()
            
            # Send notification to athlete (could be implemented with Django signals)
            
            messages.success(request, f"Appointment request {appointment.status}.")
            return redirect('manage_appointment_requests')
    else:
        form = AppointmentResponseForm(instance=appointment)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    
    return render(request, 'Dashboards/Common/respond_to_appointment.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Cancel an existing appointment"""
    # Check if user is athlete or specialist
    if request.user.user_type == 'athlete':
        appointment = get_object_or_404(
            AppointmentRequest, 
            id=appointment_id,
            athlete=request.user,
            status__in=['pending', 'accepted']
        )
    else:
        appointment = get_object_or_404(
            AppointmentRequest, 
            id=appointment_id,
            specialist=request.user,
            status='accepted'
        )
    
    # Check if appointment can be canceled (24 hours before)
    if not appointment.can_be_canceled():
        messages.error(request, "Appointments can only be canceled at least 24 hours in advance.")
        return redirect('appointments')
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        appointment.status = 'canceled'
        appointment.response_message = f"Canceled reason: {reason}"
        appointment.save()
        
        # Send notification to other party
        
        messages.success(request, "Appointment has been canceled.")
        if request.user.user_type == 'athlete':
            return redirect('appointments')
        else:
            return redirect('manage_appointment_requests')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'Dashboards/Common/cancel_appointment.html', context)

@login_required
def complete_appointment(request, appointment_id):
    """Mark an appointment as completed (specialist only)"""
    appointment = get_object_or_404(
        AppointmentRequest, 
        id=appointment_id,
        specialist=request.user,
        status='accepted'
    )
    
    # Check if appointment date has passed
    appointment_datetime = timezone.make_aware(
        timezone.datetime.combine(appointment.date, appointment.time)
    )
    if appointment_datetime > timezone.now():
        messages.error(request, "Cannot mark a future appointment as completed.")
        return redirect('manage_appointment_requests')
    
    appointment.status = 'completed'
    appointment.save()
    
    # Send notification to athlete to leave a review
    
    messages.success(request, "Appointment marked as completed.")
    return redirect('manage_appointment_requests')

@login_required
def appointment_notes(request, appointment_id):
    """Add or view notes for an appointment"""
    # Determine if user is athlete or specialist
    if request.user.user_type == 'athlete':
        appointment = get_object_or_404(
            AppointmentRequest, 
            id=appointment_id,
            athlete=request.user
        )
    else:
        appointment = get_object_or_404(
            AppointmentRequest, 
            id=appointment_id,
            specialist=request.user
        )
    
    # Get existing notes
    if request.user.user_type == 'athlete':
        notes = appointment.notes.filter(
            Q(author=request.user) | Q(is_private=False)
        )
    else:
        notes = appointment.notes.filter(author=request.user)
    
    if request.method == 'POST':
        form = AppointmentNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.appointment = appointment
            note.author = request.user
            note.save()
            
            messages.success(request, "Note added successfully.")
            return redirect('appointment_notes', appointment_id=appointment_id)
    else:
        form = AppointmentNoteForm()
    
    context = {
        'appointment': appointment,
        'notes': notes,
        'form': form,
    }
    
    return render(request, 'Dashboards/Common/appointment_notes.html', context)

@login_required
def review_appointment(request, appointment_id):
    """Leave a review for a completed appointment (athlete only)"""
    appointment = get_object_or_404(
        AppointmentRequest, 
        id=appointment_id,
        athlete=request.user,
        status='completed'
    )
    
    # Check if already reviewed
    try:
        review = appointment.review
        messages.info(request, "You have already reviewed this appointment.")
        return redirect('appointments')
    except AppointmentReview.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = AppointmentReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.save()
            
            messages.success(request, "Thank you for your review!")
            return redirect('appointments')
    else:
        form = AppointmentReviewForm()
    
    context = {
        'appointment': appointment,
        'form': form,
    }
    
    return render(request, 'Dashboards/Athlete/Appointments/review_appointment.html', context)

# Helper functions
def get_available_slots(specialist):
    """Get available time slots for a specialist"""
    # This would need to be implemented based on your scheduling requirements
    # For now, return a placeholder structure
    available_dates = []
    
    # Get specialist's profile for availability settings
    try:
        profile = specialist.specialist_profile
        availability = profile.availability
    except SpecialistProfile.DoesNotExist:
        availability = {}
    
    # Get current date and next 14 days
    start_date = timezone.now().date()
    for i in range(14):  # Next 14 days
        date = start_date + timezone.timedelta(days=i)
        
        # Skip weekends or unavailable days based on specialist's settings
        day_of_week = date.strftime('%A').lower()
        if day_of_week in availability and availability[day_of_week]:
            # Get time slots for this day
            time_slots = []
            day_slots = availability.get(day_of_week, [])
            
            # Add some demo slots if none defined
            if not day_slots:
                if day_of_week in ['monday', 'wednesday', 'friday']:
                    time_slots = ['09:00', '10:00', '11:00', '14:00', '15:00']
                else:
                    time_slots = ['13:00', '14:00', '15:00', '16:00']
            else:
                time_slots = day_slots
                
            # Check existing appointments to remove booked slots
            booked_appointments = AppointmentRequest.objects.filter(
                specialist=specialist,
                date=date,
                status__in=['pending', 'accepted']
            )
            
            booked_times = [appt.time.strftime('%H:%M') for appt in booked_appointments]
            available_times = [time for time in time_slots if time not in booked_times]
            
            if available_times:
                available_dates.append({
                    'date': date,
                    'weekday': date.strftime('%A'),
                    'times': available_times
                })
    
    return available_dates

def generate_video_session_link():
    """Generate a link for video session"""
    # This would integrate with your video conferencing provider
    return f"https://meet.yourdomain.com/{timezone.now().timestamp()}"

def generate_session_password():
    """Generate a secure password for video sessions"""
    import random
    import string
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

@login_required
def join_video_session(request, appointment_id):
    """Join a video session for an appointment"""
    # Check if user is part of this appointment
    if request.user.user_type == 'athlete':
        appointment = get_object_or_404(
            AppointmentRequest, 
            id=appointment_id,
            athlete=request.user,
            status='accepted'
        )
    else:
        appointment = get_object_or_404(
            AppointmentRequest, 
            id=appointment_id,
            specialist=request.user,
            status='accepted'
        )
    
    # Check if this is a test connection
    is_test = request.GET.get('test', 'false').lower() == 'true'
    
    if not is_test:
        # Check if appointment time is valid (allow joining 10 minutes before)
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(appointment.date, appointment.time)
        )
        time_diff = (appointment_datetime - timezone.now()).total_seconds()
        
        # Allow joining from 10 minutes before until 30 minutes after the scheduled end
        can_join = (-600 <= time_diff <= (appointment.duration * 60) + 1800)
        
        if not can_join:
            messages.error(request, "You can only join the session 10 minutes before your scheduled time and up to 30 minutes after the scheduled end.")
            if request.user.user_type == 'athlete':
                return redirect('appointments')
            else:
                return redirect('manage_appointment_requests')
    
    # Generate room details if not already created
    if not appointment.jitsi_room_created:
        jitsi_details = appointment.generate_jitsi_room_details()
    else:
        jitsi_details = {
            'room_id': appointment.jitsi_room_id,
            'password': appointment.jitsi_room_password
        }
    
    # Get user details for Jitsi
    user_display_name = request.user.get_full_name()
    user_email = request.user.email
    user_avatar = request.user.get_avatar_url() if hasattr(request.user, 'get_avatar_url') else ""
    
    # Get other participant info
    if request.user.user_type == 'athlete':
        other_participant = appointment.specialist
        participant_type = "athlete"
    else:
        other_participant = appointment.athlete
        participant_type = "specialist"
    
    other_participant_name = other_participant.get_full_name()
    
    context = {
        'appointment': appointment,
        'room_id': jitsi_details['room_id'],
        'room_password': jitsi_details['password'],
        'user_display_name': user_display_name,
        'user_email': user_email,
        'user_avatar': user_avatar,
        'participant_type': participant_type,
        'other_participant_name': other_participant_name,
        'is_test': is_test,
    }
    
    return render(request, 'Dashboards/Common/video_session.html', context)

# athlete Assessment

@login_required
def Assessments(request):
    """Athlete view for assessments"""
    # Get all available assessments for this athlete
    public_assessments = Assessment.objects.filter(
        status='published',
        is_public=True
    )
    
    # Get assessments assigned to this athlete
    assigned_assessments = Assessment.objects.filter(
        assignedassessment__athlete=request.user,
        assignedassessment__completed=False
    ).distinct()
    
    # Get previously taken assessments
    completed_assessments = Assessment.objects.filter(
        responses__athlete=request.user,
        responses__status__in=['completed', 'reviewed']
    ).distinct()
    
    context = {
        'public_assessments': public_assessments,
        'assigned_assessments': assigned_assessments,
        'completed_assessments': completed_assessments
    }
    
    return render(request, 'Dashboards/Athlete/ Mental Assessments/Assessments.html', context)

@login_required
def assessment_detail(request, assessment_id):
    """View assessment details"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if user can access this assessment
    if not assessment.is_available_for_user(request.user):
        return HttpResponseForbidden("You don't have access to this assessment.")
    
    # Check if there's an existing response in progress
    in_progress_response = AssessmentResponse.objects.filter(
        assessment=assessment,
        athlete=request.user,
        status='in_progress'
    ).first()
    
    # Check if there's an assignment
    assignment = None
    if request.user.user_type == 'athlete':
        assignment = AssignedAssessment.objects.filter(
            assessment=assessment,
            athlete=request.user,
            completed=False
        ).first()
    
    # Get previous responses
    previous_responses = None
    if request.user.user_type == 'athlete':
        previous_responses = AssessmentResponse.objects.filter(
            assessment=assessment,
            athlete=request.user,
            status__in=['completed', 'reviewed']
        )
    
    context = {
        'assessment': assessment,
        'in_progress_response': in_progress_response,
        'assignment': assignment,
        'previous_responses': previous_responses
    }
    
    return render(request, 'Dashboards/Athlete/ Mental Assessments/assessment_detail.html', context)

@login_required
def start_assessment(request, assessment_id):
    """Start a new assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Check if user can access this assessment
    if not assessment.is_available_for_user(request.user):
        return HttpResponseForbidden("You don't have access to this assessment.")
    
    # Check if user is an athlete
    if request.user.user_type != 'athlete':
        return HttpResponseForbidden("Only athletes can take assessments.")
    
    # Check if there's an existing response in progress
    in_progress_response = AssessmentResponse.objects.filter(
        assessment=assessment,
        athlete=request.user,
        status='in_progress'
    ).first()
    
    if in_progress_response:
        # Continue existing response
        return redirect('continue_assessment', response_id=in_progress_response.id)
    
    # Check if user can retake this assessment
    if not assessment.allow_retake:
        completed_response = AssessmentResponse.objects.filter(
            assessment=assessment,
            athlete=request.user,
            status__in=['completed', 'reviewed']
        ).exists()
        
        if completed_response:
            return HttpResponseForbidden("This assessment cannot be retaken.")
    
    # Check minimum days between retakes
    if assessment.minimum_days_between_retakes > 0:
        import datetime
        from django.utils import timezone
        
        last_response = AssessmentResponse.objects.filter(
            assessment=assessment,
            athlete=request.user,
            status__in=['completed', 'reviewed']
        ).order_by('-completed_at').first()
        
        if last_response and last_response.completed_at:
            days_since_last = (timezone.now() - last_response.completed_at).days
            if days_since_last < assessment.minimum_days_between_retakes:
                days_to_wait = assessment.minimum_days_between_retakes - days_since_last
                return render(request, 'Dashboards/Athlete/ Mental Assessments/retake_not_available.html', {
                    'assessment': assessment,
                    'days_to_wait': days_to_wait,
                    'available_date': last_response.completed_at + datetime.timedelta(days=assessment.minimum_days_between_retakes)
                })
    
    # Check if this is from an assignment
    assignment = None
    if request.user.user_type == 'athlete':
        assignment = AssignedAssessment.objects.filter(
            assessment=assessment,
            athlete=request.user,
            completed=False
        ).first()
    
    # Create new response
    response = AssessmentResponse.objects.create(
        assessment=assessment,
        athlete=request.user,
        status='in_progress',
        assignment=assignment
    )
    
    return redirect('continue_assessment', response_id=response.id)

@login_required
def continue_assessment(request, response_id):
    """Continue an assessment in progress"""
    response = get_object_or_404(AssessmentResponse, id=response_id)
    
    # Security check
    if response.athlete != request.user:
        return HttpResponseForbidden("You don't have access to this assessment response.")
    
    # Check if already completed
    if response.status != 'in_progress':
        return redirect('view_results', response_id=response.id)
    
    # Get assessment and questions
    assessment = response.assessment
    questions = assessment.questions.all().order_by('order')
    
    # Get already answered questions
    answered_questions = {qr.question_id: qr.answer_value for qr in response.question_responses.all()}
    
    context = {
        'assessment': assessment,
        'questions': questions,
        'response': response,
        'answered_questions': answered_questions
    }
    
    return render(request, 'Dashboards/Athlete/ Mental Assessments/take_assessment.html', context)

@login_required
@require_POST
def save_question_response(request, response_id):
    """Save response to a single question"""
    response = get_object_or_404(AssessmentResponse, id=response_id)
    
    # Security check
    if response.athlete != request.user:
        return HttpResponseForbidden("You don't have access to this assessment response.")
    
    # Check if already completed
    if response.status != 'in_progress':
        return JsonResponse({'status': 'error', 'message': 'Assessment already completed'})
    
    # Get question and answer
    question_id = request.POST.get('question_id')
    answer_value = request.POST.get('answer_value')
    
    question = get_object_or_404(Question, id=question_id)
    
    # Validate that question belongs to this assessment
    if question.assessment_id != response.assessment_id:
        return JsonResponse({'status': 'error', 'message': 'Question does not belong to this assessment'})
    
    # Create or update question response
    question_response, created = QuestionResponse.objects.update_or_create(
        assessment_response=response,
        question=question,
        defaults={'answer_value': answer_value}
    )
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def complete_assessment(request, response_id):
    """Complete an assessment and calculate scores"""
    response = get_object_or_404(AssessmentResponse, id=response_id)
    
    # Security check
    if response.athlete != request.user:
        return HttpResponseForbidden("You don't have access to this assessment response.")
    
    # Check if already completed
    if response.status != 'in_progress':
        return JsonResponse({'status': 'error', 'message': 'Assessment already completed'})
    
    # Check if all required questions are answered
    required_questions = response.assessment.questions.filter(required=True)
    answered_questions = response.question_responses.values_list('question_id', flat=True)
    
    missing_questions = []
    for question in required_questions:
        if question.id not in answered_questions:
            missing_questions.append(question.id)
    
    if missing_questions:
        return JsonResponse({
            'status': 'error', 
            'message': 'Not all required questions have been answered',
            'missing_questions': missing_questions
        })
    
    # Calculate scores
    scores = response.calculate_scores()
    
    # Generate recommendations
    if response.status == 'completed':
        recommendation_engine = RecommendationEngine(response)
        recommendation_engine.save_recommendations()
    
    return JsonResponse({
        'status': 'success',
        'redirect_url': reverse('view_results', args=[response_id])
    })

@login_required
def view_results(request, response_id):
    """View assessment results"""
    response = get_object_or_404(AssessmentResponse, id=response_id)
    
    # Security check
    if response.athlete != request.user and response.assessment.creator != request.user:
        # Check if psychologist has permission to view
        has_permission = False
        if request.user.user_type == 'psychologist':
            if response.assignment and response.assignment.assigned_by == request.user:
                has_permission = True
        
        if not has_permission:
            return HttpResponseForbidden("You don't have access to these results.")
    
    # Check if results can be shown
    if not response.assessment.show_results_immediately and response.status != 'reviewed':
        if request.user != response.athlete:
            # Psychologists can always see results
            pass
        else:
            return render(request, 'Dashboards/Athlete/ Mental Assessments/results_not_available.html', {
                'response': response
            })
    
    # Get review
    review = None
    try:
        review = response.psychologist_review
    except:
        pass
    
    # Get recommendations
    recommendations = response.recommended_specialists.all()
    
    context = {
        'response': response,
        'assessment': response.assessment,
        'scores': response.scores,
        'review': review,
        'recommendations': recommendations
    }
    
    return render(request, 'Dashboards/Athlete/ Mental Assessments/assessment_results.html', context)

@login_required
def psychologist_review(request, response_id):
    """Create or edit a psychologist review"""
    response = get_object_or_404(AssessmentResponse, id=response_id)
    
    # Security check
    if request.user.user_type != 'psychologist':
        return HttpResponseForbidden("Only psychologists can create reviews.")
    
    # Check if psychologist has permission
    has_permission = False
    if response.assessment.creator == request.user:
        has_permission = True
    elif response.assignment and response.assignment.assigned_by == request.user:
        has_permission = True
    
    if not has_permission:
        return HttpResponseForbidden("You don't have permission to review this assessment.")
    
    # Get or create review
    review, created = PsychologistReview.objects.get_or_create(
        assessment_response=response,
        defaults={'psychologist': request.user}
    )
    
    if request.method == 'POST':
        # Update review
        review.comments = request.POST.get('comments', '')
        review.recommendations = request.POST.get('recommendations', '')
        review.follow_up_needed = request.POST.get('follow_up_needed') == 'on'
        
        # Handle score adjustments
        score_adjustments = {}
        for key, value in request.POST.items():
            if key.startswith('score_adjustment_'):
                scale_name = key.replace('score_adjustment_', '')
                try:
                    score_adjustments[scale_name] = float(value)
                except:
                    pass
        
        if score_adjustments:
            review.score_adjustments = score_adjustments
        
        review.save()
        
        # Update response status
        response.status = 'reviewed'
        response.save()
        
        return redirect('view_results', response_id=response.id)
    
    context = {
        'response': response,
        'assessment': response.assessment,
        'scores': response.scores,
        'review': review
    }
    
    return render(request, 'Dashboards/Psychologist/Mental Assessments/psychologist_review.html', context)

@login_required
def psychologist_assign_assessment(request, athlete_id=None):
    """Assign an assessment to an athlete"""
    if request.user.user_type != 'psychologist':
        return HttpResponseForbidden("Only psychologists can assign assessments.")
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get athlete if specified
    athlete = None
    if athlete_id:
        athlete = get_object_or_404(User, id=athlete_id, user_type='athlete')
    
    # Get athletes this psychologist has access to
    athletes = User.objects.filter(user_type='athlete')
    
    # Get assessments this psychologist can assign
    assessments = Assessment.objects.filter(
        Q(creator=request.user) | Q(is_public=True),
        status='published'
    )
    
    if request.method == 'POST':
        assessment_id = request.POST.get('assessment')
        athlete_ids = request.POST.getlist('athletes')
        due_date = request.POST.get('due_date')
        instructions = request.POST.get('instructions')
        
        # Validate assessment
        assessment = get_object_or_404(Assessment, id=assessment_id)
        if assessment.creator != request.user and not assessment.is_public:
            return HttpResponseForbidden("You don't have permission to assign this assessment.")
        
        # Create assignments
        assignments_created = 0
        for athlete_id in athlete_ids:
            try:
                athlete = User.objects.get(id=athlete_id, user_type='athlete')
                
                # Create assignment
                AssignedAssessment.objects.create(
                    assessment=assessment,
                    athlete=athlete,
                    assigned_by=request.user,
                    due_date=due_date if due_date else None,
                    instructions=instructions
                )
                
                assignments_created += 1
            except:
                pass
        
        return render(request, 'Dashboards/Psychologist/Mental Assessments/assignment_success.html', {
            'assessment': assessment,
            'count': assignments_created
        })
    
    context = {
        'athletes': athletes,
        'assessments': assessments,
        'selected_athlete': athlete
    }
    
    return render(request, 'Dashboards/Psychologist/Mental Assessments/assign_assessment.html', context)

@login_required
def athlete_progress(request, athlete_id=None):
    """View an athlete's progress over time"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Determine which athlete to show
    athlete = None
    if athlete_id:
        athlete = get_object_or_404(User, id=athlete_id, user_type='athlete')
        
        # Security check
        if request.user.user_type not in ['psychologist', 'coach', 'admin'] and request.user != athlete:
            return HttpResponseForbidden("You don't have permission to view this athlete's progress.")
    else:
        # Default to current user if they're an athlete
        if request.user.user_type == 'athlete':
            athlete = request.user
        else:
            return HttpResponseForbidden("Please specify which athlete's progress to view.")
    
    # Get assessment responses
    responses = AssessmentResponse.objects.filter(
        athlete=athlete,
        status__in=['completed', 'reviewed']
    ).order_by('-completed_at')
    
    # Get progress metrics
    metrics = AthleteMetricProgress.objects.filter(
        athlete=athlete
    ).order_by('-date')
    
    # Get assessment categories
    categories = AssessmentCategory.objects.filter(
        assessments__responses__athlete=athlete,
        assessments__responses__status__in=['completed', 'reviewed']
    ).distinct()
    
    context = {
        'athlete': athlete,
        'responses': responses,
        'metrics': metrics,
        'categories': categories
    }
    
    return render(request, 'Dashboards/Athlete/ Mental Assessments/athlete_progress.html', context)

# Add this to views.py for psy
@login_required
def create_assessment(request):
    """Create a new assessment"""
    if request.user.user_type != 'psychologist':
        return HttpResponseForbidden("Only psychologists can create assessments.")
    
    # Get categories for form
    categories = AssessmentCategory.objects.all()
    
    if request.method == 'POST':
        # Process form submission
        title = request.POST.get('title')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        difficulty = request.POST.get('difficulty_level', 'intermediate')
        is_public = request.POST.get('is_public') == 'on'
        show_results = request.POST.get('show_results_immediately') == 'on'
        require_review = request.POST.get('require_psychologist_review') == 'on'
        allow_retake = request.POST.get('allow_retake') == 'on'
        min_days = request.POST.get('minimum_days_between_retakes', 7)
        estimated_time = request.POST.get('estimated_time_minutes', 15)
        
        # Validate required fields
        if not title or not description or not category_id:
            return render(request, 'Mental Assessments/create_assessment.html', {
                'categories': categories,
                'error': 'Please fill in all required fields.',
                'form_data': request.POST
            })
        
        try:
            # Create assessment
            category = get_object_or_404(AssessmentCategory, id=category_id)
            
            assessment = Assessment.objects.create(
                title=title,
                description=description,
                category=category,
                creator=request.user,
                difficulty_level=difficulty,
                status='draft',  # Start as draft
                is_public=is_public,
                show_results_immediately=show_results,
                require_psychologist_review=require_review,
                allow_retake=allow_retake,
                minimum_days_between_retakes=int(min_days),
                estimated_time_minutes=int(estimated_time)
            )
            
            return redirect('edit_assessment', assessment_id=assessment.id)
        except Exception as e:
            return render(request, 'Mental Assessments/create_assessment.html', {
                'categories': categories,
                'error': f'Error creating assessment: {str(e)}',
                'form_data': request.POST
            })
    
    return render(request, 'Dashboards/Psychologist/Mental Assessments/create_assessment.html', {
        'categories': categories
    })

@login_required
def edit_assessment(request, assessment_id):
    """Edit an existing assessment"""
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Security check
    if assessment.creator != request.user:
        return HttpResponseForbidden("You don't have permission to edit this assessment.")
    
    # Get categories and existing questions
    categories = AssessmentCategory.objects.all()
    questions = assessment.questions.all().order_by('order')
    scales = assessment.scales.all()
    
    if request.method == 'POST':
        # Handle the update logic here based on form submission
        action = request.POST.get('action', '')
        
        if action == 'update_assessment':
            # Update assessment details
            assessment.title = request.POST.get('title', assessment.title)
            assessment.description = request.POST.get('description', assessment.description)
            
            category_id = request.POST.get('category')
            if category_id:
                assessment.category = get_object_or_404(AssessmentCategory, id=category_id)
            
            assessment.difficulty_level = request.POST.get('difficulty_level', assessment.difficulty_level)
            assessment.is_public = request.POST.get('is_public') == 'on'
            assessment.show_results_immediately = request.POST.get('show_results_immediately') == 'on'
            assessment.require_psychologist_review = request.POST.get('require_psychologist_review') == 'on'
            assessment.allow_retake = request.POST.get('allow_retake') == 'on'
            
            min_days = request.POST.get('minimum_days_between_retakes')
            if min_days:
                assessment.minimum_days_between_retakes = int(min_days)
            
            estimated_time = request.POST.get('estimated_time_minutes')
            if estimated_time:
                assessment.estimated_time_minutes = int(estimated_time)
            
            assessment.save()
            
            return redirect('edit_assessment', assessment_id=assessment.id)
        
        elif action == 'add_question':
            # Logic to add a new question
            text = request.POST.get('question_text')
            question_type = request.POST.get('question_type')
            required = request.POST.get('required') == 'on'
            help_text = request.POST.get('help_text', '')
            
            # Set order to be last
            order = assessment.questions.count() + 1
            
            # Create the question
            question = Question.objects.create(
                assessment=assessment,
                text=text,
                question_type=question_type,
                required=required,
                help_text=help_text,
                order=order
            )
            
            # Handle specific question type details
            if question_type == 'multiple_choice':
                choices = []
                for i in range(1, 10):  # Assuming max 10 choices
                    choice = request.POST.get(f'choice_{i}')
                    if choice:
                        choices.append(choice)
                
                if choices:
                    question.choices = choices
                    question.save()
            
            elif question_type in ['slider', 'likert_5', 'likert_7']:
                min_value = request.POST.get('min_value')
                max_value = request.POST.get('max_value')
                step = request.POST.get('step')
                
                if min_value:
                    question.min_value = int(min_value)
                if max_value:
                    question.max_value = int(max_value)
                if step:
                    question.step = float(step)
                
                question.save()
            
            return redirect('edit_assessment', assessment_id=assessment.id)
        
        elif action == 'add_scale':
            # Logic to add a scoring scale
            scale_name = request.POST.get('scale_name')
            scale_description = request.POST.get('scale_description')
            min_score = request.POST.get('min_score')
            max_score = request.POST.get('max_score')
            
            # Create ranges
            ranges = []
            for i in range(1, 5):  # Assuming max 5 ranges
                range_min = request.POST.get(f'range_{i}_min')
                range_max = request.POST.get(f'range_{i}_max')
                range_label = request.POST.get(f'range_{i}_label')
                range_description = request.POST.get(f'range_{i}_description')
                
                if range_min and range_max and range_label:
                    ranges.append({
                        'min': float(range_min),
                        'max': float(range_max),
                        'label': range_label,
                        'description': range_description or ''
                    })
            
            if scale_name and min_score and max_score and ranges:
                ResponseScale.objects.create(
                    assessment=assessment,
                    name=scale_name,
                    description=scale_description or '',
                    min_score=float(min_score),
                    max_score=float(max_score),
                    ranges=ranges
                )
            
            return redirect('edit_assessment', assessment_id=assessment.id)
        
        elif action == 'publish':
            # Publish the assessment
            # First check if it has questions
            if assessment.questions.count() > 0:
                assessment.status = 'published'
                assessment.save()
                return redirect('PsychologistAssessments')
            else:
                return render(request, 'Mental Assessments/edit_assessment.html', {
                    'assessment': assessment,
                    'categories': categories,
                    'questions': questions,
                    'scales': scales,
                    'error': 'Cannot publish assessment with no questions.'
                })
    
    return render(request, 'Dashboards/Psychologist/Mental Assessments/edit_assessment.html', {
        'assessment': assessment,
        'categories': categories,
        'questions': questions,
        'scales': scales
    })

@login_required
@require_POST
def delete_question(request, question_id):
    """Delete a question from an assessment"""
    question = get_object_or_404(Question, id=question_id)
    assessment = question.assessment
    
    # Security check
    if assessment.creator != request.user:
        return HttpResponseForbidden("You don't have permission to edit this assessment.")
    
    # Check if assessment is published
    if assessment.status == 'published':
        # Check if the assessment has responses
        if assessment.responses.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot delete questions from an assessment with existing responses.'
            })
    
    # Delete the question
    question.delete()
    
    # Reorder remaining questions
    for i, q in enumerate(assessment.questions.all().order_by('order')):
        q.order = i + 1
        q.save()
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def delete_scale(request, scale_id):
    """Delete a scale from an assessment"""
    scale = get_object_or_404(ResponseScale, id=scale_id)
    assessment = scale.assessment
    
    # Security check
    if assessment.creator != request.user:
        return HttpResponseForbidden("You don't have permission to edit this assessment.")
    
    # Check if assessment is published
    if assessment.status == 'published':
        # Check if the assessment has responses
        if assessment.responses.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot delete scales from an assessment with existing responses.'
            })
    
    # Delete the scale
    scale.delete()
    
    return JsonResponse({'status': 'success'})

@login_required
def duplicate_assessment(request, assessment_id):
    """Create a copy of an existing assessment"""
    original = get_object_or_404(Assessment, id=assessment_id)
    
    # Check permission
    has_permission = False
    if original.creator == request.user:
        has_permission = True
    elif original.is_public:
        has_permission = True
    
    if not has_permission:
        return HttpResponseForbidden("You don't have permission to duplicate this assessment.")
    
    # Create a copy of the assessment
    new_assessment = Assessment.objects.create(
        title=f"Copy of {original.title}",
        description=original.description,
        category=original.category,
        creator=request.user,
        difficulty_level=original.difficulty_level,
        status='draft',  # Always start as draft
        is_public=False,  # Default to private for copied assessments
        estimated_time_minutes=original.estimated_time_minutes,
        show_results_immediately=original.show_results_immediately,
        require_psychologist_review=original.require_psychologist_review,
        allow_retake=original.allow_retake,
        minimum_days_between_retakes=original.minimum_days_between_retakes
    )
    
    # Copy questions
    for question in original.questions.all():
        new_question = Question.objects.create(
            assessment=new_assessment,
            text=question.text,
            help_text=question.help_text,
            question_type=question.question_type,
            required=question.required,
            order=question.order,
            reverse_scoring=question.reverse_scoring,
            weight=question.weight,
            choices=question.choices,
            min_value=question.min_value,
            max_value=question.max_value,
            step=question.step
        )
    
    # Copy scales
    for scale in original.scales.all():
        new_scale = ResponseScale.objects.create(
            assessment=new_assessment,
            name=scale.name,
            description=scale.description,
            min_score=scale.min_score,
            max_score=scale.max_score,
            ranges=scale.ranges
        )
    
    return redirect('edit_assessment', assessment_id=new_assessment.id)



# Wellness Resources Views
@login_required
def WellnessResources(request):
    """Main wellness resources page with categories and featured resources"""
    categories = ResourceCategory.objects.all()
    featured_resources = WellnessResource.objects.filter(published=True, featured=True)[:5]
    recent_resources = WellnessResource.objects.filter(published=True).order_by('-created_at')[:10]
    
    # Get saved resources for this user
    saved_resource_ids = SavedResource.objects.filter(user=request.user).values_list('resource_id', flat=True)
    
    context = {
        'categories': categories,
        'featured_resources': featured_resources,
        'recent_resources': recent_resources,
        'saved_resource_ids': list(saved_resource_ids),
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/WellnessResources.html', context)

@login_required
def resource_category(request, slug):
    """Display resources for a specific category"""
    category = get_object_or_404(ResourceCategory, slug=slug)
    resources = WellnessResource.objects.filter(category=category, published=True)
    
    # Filter resources if search query is provided
    query = request.GET.get('q')
    if query:
        resources = resources.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(tags__icontains=query)
        )
    
    # Get saved resources for this user
    saved_resource_ids = SavedResource.objects.filter(user=request.user).values_list('resource_id', flat=True)
    
    # Pagination
    paginator = Paginator(resources, 12)  # 12 resources per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'saved_resource_ids': list(saved_resource_ids),
        'query': query,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/category.html', context)

@login_required
def resource_detail(request, slug):
    """Display a specific resource"""
    resource = get_object_or_404(WellnessResource, slug=slug, published=True)
    
    # Increment view count
    resource.increment_view_count()
    
    # Check if user has saved this resource
    is_saved = SavedResource.objects.filter(user=request.user, resource=resource).exists()
    
    # Get user's rating if exists
    try:
        user_rating = ResourceRating.objects.get(user=request.user, resource=resource)
    except ResourceRating.DoesNotExist:
        user_rating = None
    
    # Get average rating
    avg_rating = ResourceRating.objects.filter(resource=resource).aggregate(Avg('rating'))['rating__avg']
    
    # Get related resources
    related_resources = resource.related_resources.filter(published=True)
    
    context = {
        'resource': resource,
        'is_saved': is_saved,
        'user_rating': user_rating,
        'avg_rating': avg_rating,
        'related_resources': related_resources,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/detail.html', context)

@login_required
@require_POST
def save_resource(request):
    """Save/bookmark a resource for a user"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        resource_id = request.POST.get('resource_id')
        
        if not resource_id:
            return JsonResponse({'status': 'error', 'message': 'Resource ID is required'}, status=400)
        
        try:
            resource = WellnessResource.objects.get(id=resource_id, published=True)
        except WellnessResource.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Resource not found'}, status=404)
        
        # Check if already saved
        saved, created = SavedResource.objects.get_or_create(user=request.user, resource=resource)
        
        if created:
            return JsonResponse({'status': 'success', 'message': 'Resource saved successfully'})
        else:
            # If already exists, remove it (toggle behavior)
            saved.delete()
            return JsonResponse({'status': 'success', 'message': 'Resource removed from saved items'})
    
    return HttpResponseBadRequest("Invalid request")

@login_required
def saved_resources(request):
    """View all resources saved by the user"""
    saved_items = SavedResource.objects.filter(user=request.user).select_related('resource')
    
    context = {
        'saved_items': saved_items,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/saved.html', context)

@login_required
@require_POST
def rate_resource(request):
    """Rate a resource"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        resource_id = request.POST.get('resource_id')
        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback', '')
        
        if not resource_id or not rating:
            return JsonResponse({'status': 'error', 'message': 'Resource ID and rating are required'}, status=400)
        
        try:
            resource = WellnessResource.objects.get(id=resource_id, published=True)
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
        except (WellnessResource.DoesNotExist, ValueError) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        
        # Update or create rating
        rating_obj, created = ResourceRating.objects.update_or_create(
            user=request.user,
            resource=resource,
            defaults={
                'rating': rating,
                'feedback': feedback
            }
        )
        
        # Calculate new average
        avg_rating = ResourceRating.objects.filter(resource=resource).aggregate(Avg('rating'))['rating__avg']
        
        return JsonResponse({
            'status': 'success', 
            'message': 'Rating submitted successfully',
            'avg_rating': avg_rating
        })
    
    return HttpResponseBadRequest("Invalid request")

@login_required
def search_resources(request):
    """Search for resources across all categories"""
    query = request.GET.get('q', '')
    
    if query:
        resources = WellnessResource.objects.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) | 
            Q(tags__icontains=query) | 
            Q(content__icontains=query),
            published=True
        )
    else:
        resources = WellnessResource.objects.none()
    
    # Get saved resources for this user
    saved_resource_ids = SavedResource.objects.filter(user=request.user).values_list('resource_id', flat=True)
    
    # Pagination
    paginator = Paginator(resources, 12)  # 12 resources per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'saved_resource_ids': list(saved_resource_ids),
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/search.html', context)

# Journal Views
@login_required
def journal_home(request):
    """Journal home page with recent entries and stats"""
    # Get recent entries
    recent_entries = JournalEntry.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Get stats
    total_entries = JournalEntry.objects.filter(user=request.user).count()
    streak = calculate_streak(request.user)
    entries_this_month = JournalEntry.objects.filter(
        user=request.user,
        date__year=timezone.now().year,
        date__month=timezone.now().month
    ).count()
    
    # Get a random prompt
    prompt = JournalPrompt.objects.filter(is_active=True).order_by('?').first()
    
    # Check if there's an entry for today
    today = timezone.now().date()
    has_entry_today = JournalEntry.objects.filter(user=request.user, date=today).exists()
    
    context = {
        'recent_entries': recent_entries,
        'total_entries': total_entries,
        'streak': streak,
        'entries_this_month': entries_this_month,
        'prompt': prompt,
        'has_entry_today': has_entry_today,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/journal_home.html', context)

def calculate_streak(user):
    """Calculate the current journaling streak for a user"""
    today = timezone.now().date()
    entries = JournalEntry.objects.filter(
        user=user,
        date__lte=today
    ).order_by('-date').values_list('date', flat=True)
    
    if not entries:
        return 0
    
    # Check if there's an entry for today or yesterday
    if entries[0] < today - timedelta(days=1):
        return 0  # Streak is broken
    
    streak = 1
    prev_date = entries[0]
    
    for date in entries[1:]:
        if prev_date - date == timedelta(days=1):
            streak += 1
            prev_date = date
        else:
            break
    
    return streak

@login_required
def new_journal_entry(request):
    """Create a new journal entry"""
    today = timezone.now().date()
    
    # Check if entry for today already exists
    existing_entry = JournalEntry.objects.filter(user=request.user, date=today).first()
    if existing_entry:
        messages.info(request, "You've already created an entry for today. You can edit it instead.")
        return redirect('edit_journal_entry', entry_id=existing_entry.id)
    
    # Get available templates
    templates = JournalTemplate.objects.filter(
        Q(is_public=True) | Q(created_by__exact=request.user)
    )
    
    # Get a random prompt
    prompt = JournalPrompt.objects.filter(is_active=True).order_by('?').first()
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        mood = request.POST.get('mood')
        energy_level = request.POST.get('energy_level')
        stress_level = request.POST.get('stress_level')
        sleep_hours = request.POST.get('sleep_hours')
        tags = request.POST.get('tags')
        is_private = request.POST.get('is_private', 'on') == 'on'
        
        # Validate required fields
        if not content or not mood:
            messages.error(request, "Please fill in all required fields")
            return render(request, 'Dashboards/Athlete/WellnessResources/new_journal_entry.html', {
                'templates': templates,
                'prompt': prompt
            })
        
        # Create the entry
        entry = JournalEntry.objects.create(
            user=request.user,
            date=today,
            title=title,
            content=content,
            mood=mood,
            energy_level=energy_level,
            stress_level=stress_level,
            sleep_hours=float(sleep_hours) if sleep_hours else None,
            tags=tags,
            is_private=is_private
        )
        
        # Process shared_with if not private
        if not is_private:
            shared_with_ids = request.POST.getlist('shared_with')
            if shared_with_ids:
                entry.shared_with.set(shared_with_ids)
        
        messages.success(request, "Journal entry created successfully!")
        return redirect('journal_home')
    
    context = {
        'templates': templates,
        'prompt': prompt,
        'today': today,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/new_journal_entry.html', context)

@login_required
def edit_journal_entry(request, entry_id):
    """Edit an existing journal entry"""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        # Process form data
        entry.title = request.POST.get('title')
        entry.content = request.POST.get('content')
        
        # Ensure required fields are provided
        mood = request.POST.get('mood')
        if not mood:
            messages.error(request, "Mood selection is required")
            return render(request, 'Dashboards/Athlete/WellnessResources/edit_journal_entry.html', {
                'entry': entry,
                'shared_with': list(entry.shared_with.values_list('id', flat=True)),
            })
        
        entry.mood = mood
        entry.energy_level = request.POST.get('energy_level')
        entry.stress_level = request.POST.get('stress_level')
        
        sleep_hours = request.POST.get('sleep_hours')
        entry.sleep_hours = float(sleep_hours) if sleep_hours else None
        
        entry.tags = request.POST.get('tags')
        entry.is_private = request.POST.get('is_private', 'on') == 'on'
        
        # Save changes
        try:
            entry.save()
            
            # Process shared_with if not private
            if not entry.is_private:
                shared_with_ids = request.POST.getlist('shared_with')
                if shared_with_ids:
                    entry.shared_with.set(shared_with_ids)
            
            messages.success(request, "Journal entry updated successfully!")
            return redirect('view_journal_entry', entry_id=entry.id)
        except IntegrityError as e:
            messages.error(request, f"Error saving entry: {str(e)}")
            return render(request, 'Dashboards/Athlete/WellnessResources/edit_journal_entry.html', {
                'entry': entry,
                'shared_with': list(entry.shared_with.values_list('id', flat=True)),
            })
    
    context = {
        'entry': entry,
        'shared_with': list(entry.shared_with.values_list('id', flat=True)),
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/edit_journal_entry.html', context)

@login_required
def view_journal_entry(request, entry_id):
    """View a specific journal entry"""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    
    context = {
        'entry': entry,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/view_journal_entry.html', context)

@login_required
def journal_calendar(request):
    """Calendar view of journal entries"""
    # If AJAX request for calendar data
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        if not start_date or not end_date:
            return JsonResponse({'status': 'error', 'message': 'Start and end dates are required'}, status=400)
        
        try:
            start_date = datetime.strptime(start_date[:10], '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date[:10], '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)
        
        # Get entries within the date range
        entries = JournalEntry.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Format for calendar
        events = []
        for entry in entries:
            mood_colors = {
                'excellent': '#28a745',
                'good': '#5cb85c',
                'neutral': '#6c757d',
                'bad': '#dc3545',
                'terrible': '#9c1f2e',
            }
            
            events.append({
                'id': entry.id,
                'title': entry.title or 'Journal Entry',
                'start': entry.date.isoformat(),
                'url': reverse('view_journal_entry', args=[entry.id]),
                'backgroundColor': mood_colors.get(entry.mood, '#6c757d'),
                'borderColor': mood_colors.get(entry.mood, '#6c757d'),
            })
        
        return JsonResponse(events, safe=False)
    
    # Regular page request
    return render(request, 'Dashboards/Athlete/WellnessResources/journal_calendar.html')

@login_required
def journal_analysis(request):
    """Analysis of journal entries and mood trends"""
    # Get date range from query parameters or use last 30 days
    end_date = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    
    if start_date and end_date_param:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format. Using last 30 days instead.")
            start_date = end_date - timedelta(days=30)
    else:
        # Default to last 30 days
        start_date = end_date - timedelta(days=30)
    
    # Get entries in date range
    entries = JournalEntry.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Prepare data for charts
    dates = []
    moods = []
    energy_levels = []
    stress_levels = []
    sleep_hours = []
    
    mood_values = {
        'terrible': 1,
        'bad': 2,
        'neutral': 3,
        'good': 4,
        'excellent': 5,
    }
    
    energy_values = {
        'very_low': 1,
        'low': 2,
        'moderate': 3,
        'high': 4,
        'very_high': 5,
    }
    
    stress_values = {
        'none': 1,
        'mild': 2,
        'moderate': 3,
        'high': 4,
        'severe': 5,
    }
    
    for entry in entries:
        dates.append(entry.date.strftime('%Y-%m-%d'))
        moods.append(mood_values.get(entry.mood, 0))
        energy_levels.append(energy_values.get(entry.energy_level, 0) if entry.energy_level else None)
        stress_levels.append(stress_values.get(entry.stress_level, 0) if entry.stress_level else None)
        sleep_hours.append(float(entry.sleep_hours) if entry.sleep_hours is not None else None)
    
    # Calculate statistics
    mood_avg = sum([m for m in moods if m > 0]) / len(moods) if moods else 0
    mood_trend = "improving" if len(moods) >= 7 and sum(moods[-3:]) > sum(moods[:3]) else "stable"
    
    # Get most used tags
    all_tags = []
    for entry in entries:
        all_tags.extend(entry.get_tags_list())
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'entries': entries,
        'dates_json': json.dumps(dates),
        'moods_json': json.dumps(moods),
        'energy_levels_json': json.dumps(energy_levels),
        'stress_levels_json': json.dumps(stress_levels),
        'sleep_hours_json': json.dumps(sleep_hours),
        'mood_avg': mood_avg,
        'mood_trend': mood_trend,
        'top_tags': top_tags,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/journal_analysis.html', context)

@login_required
def journal_search(request):
    """Search journal entries"""
    query = request.GET.get('q', '')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    mood = request.GET.get('mood')
    tags = request.GET.get('tags')
    
    entries = JournalEntry.objects.filter(user=request.user)
    
    # Apply filters
    if query:
        entries = entries.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            entries = entries.filter(date__gte=date_from)
        except ValueError:
            messages.error(request, "Invalid 'from' date format")
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            entries = entries.filter(date__lte=date_to)
        except ValueError:
            messages.error(request, "Invalid 'to' date format")
    
    if mood:
        entries = entries.filter(mood=mood)
    
        if tags:
            # Split tags and search for entries containing any of the tags
            tag_list = [tag.strip() for tag in tags.split(',')]
            tag_query = Q()
            for tag in tag_list:
                tag_query |= Q(tags__icontains=tag)
            entries = entries.filter(tag_query)
    
    # Order by date, newest first
    entries = entries.order_by('-date')
    
    # Pagination
    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'date_from': date_from,
        'date_to': date_to,
        'mood': mood,
        'tags': tags,
        'page_obj': page_obj,
        'mood_choices': JournalEntry.MOOD_CHOICES,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/journal_search.html', context)

@login_required
def delete_journal_entry(request, entry_id):
    """Delete a journal entry"""
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Journal entry deleted successfully.")
        return redirect('journal_home')
    
    context = {
        'entry': entry,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/delete_journal_entry.html', context)

@login_required
def export_journal_entries(request):
    """Export journal entries as JSON or CSV"""
    format_type = request.GET.get('format', 'json')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Get date range or use all time
    entries = JournalEntry.objects.filter(user=request.user)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            entries = entries.filter(date__gte=date_from)
        except ValueError:
            messages.error(request, "Invalid 'from' date format")
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            entries = entries.filter(date__lte=date_to)
        except ValueError:
            messages.error(request, "Invalid 'to' date format")
    
    entries = entries.order_by('date')
    
    if format_type == 'json':
        # Create JSON export
        data = []
        for entry in entries:
            data.append({
                'date': entry.date.strftime('%Y-%m-%d'),
                'title': entry.title,
                'content': entry.content,
                'mood': entry.mood,
                'energy_level': entry.energy_level,
                'stress_level': entry.stress_level,
                'sleep_hours': float(entry.sleep_hours) if entry.sleep_hours is not None else None,
                'tags': entry.get_tags_list(),
                'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        response = JsonResponse(data, safe=False, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="journal_export_{timezone.now().strftime("%Y%m%d")}.json"'
        return response
    
    elif format_type == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="journal_export_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Title', 'Content', 'Mood', 'Energy Level', 'Stress Level', 'Sleep Hours', 'Tags', 'Created At'])
        
        for entry in entries:
            writer.writerow([
                entry.date.strftime('%Y-%m-%d'),
                entry.title,
                entry.content,
                entry.get_mood_display(),
                entry.get_energy_level_display() if entry.energy_level else '',
                entry.get_stress_level_display() if entry.stress_level else '',
                entry.sleep_hours if entry.sleep_hours is not None else '',
                ', '.join(entry.get_tags_list()),
                entry.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            ])
        
        return response
    
    # If invalid format, redirect to home
    messages.error(request, "Invalid export format.")
    return redirect('journal_home')

@login_required
def random_prompt(request):
    """Get a random journal prompt"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        prompt = JournalPrompt.objects.filter(is_active=True).order_by('?').first()
        
        if prompt:
            return JsonResponse({
                'status': 'success',
                'prompt': prompt.text,
                'id': prompt.id
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'No prompts available'
            }, status=404)
    
    return HttpResponseBadRequest("Invalid request")

@login_required
def journal_template_detail(request, template_id):
    """View a specific journal template"""
    template = get_object_or_404(
    JournalTemplate,
    Q(created_by=request.user) | Q(is_public=True),
    id=template_id
)
    
    context = {
        'template': template,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/journal_template_detail.html', context)

@login_required
def create_entry_from_template(request, template_id):
    """Create a new journal entry using a template"""
    template = get_object_or_404(
    JournalTemplate,
    Q(is_public=True) | Q(created_by=request.user),
    id=template_id
)
    
    today = timezone.now().date()
    
    # Check if entry for today already exists
    existing_entry = JournalEntry.objects.filter(user=request.user, date=today).first()
    if existing_entry:
        messages.info(request, "You've already created an entry for today. You can edit it instead.")
        return redirect('edit_journal_entry', entry_id=existing_entry.id)
    
    if request.method == 'POST':
        # Process form data
        title = request.POST.get('title')
        content = request.POST.get('content')
        mood = request.POST.get('mood')
        energy_level = request.POST.get('energy_level')
        stress_level = request.POST.get('stress_level')
        sleep_hours = request.POST.get('sleep_hours')
        tags = request.POST.get('tags')
        is_private = request.POST.get('is_private', 'on') == 'on'
        
        # Create the entry
        entry = JournalEntry.objects.create(
            user=request.user,
            date=today,
            title=title,
            content=content,
            mood=mood,
            energy_level=energy_level,
            stress_level=stress_level,
            sleep_hours=float(sleep_hours) if sleep_hours else None,
            tags=tags,
            is_private=is_private
        )
        
        # Process shared_with if not private
        if not is_private:
            shared_with_ids = request.POST.getlist('shared_with')
            if shared_with_ids:
                entry.shared_with.set(shared_with_ids)
        
        messages.success(request, "Journal entry created successfully!")
        return redirect('view_journal_entry', entry_id=entry.id)
    
    context = {
        'template': template,
        'today': today,
    }
    
    return render(request, 'Dashboards/Athlete/WellnessResources/create_from_template.html', context)


@receiver(post_save, sender=JournalEntry)
def notify_shared_users(sender, instance, created, **kwargs):
    """Notify professionals when an athlete shares a journal entry with them"""
    if created and not instance.is_private and instance.shared_with.exists():
        subject = f"New Journal Entry Shared by {instance.user.get_full_name()}"
        
        for professional in instance.shared_with.all():
            # Only send if user has email notifications enabled
            if hasattr(professional, 'profile') and professional.profile.email_notifications:
                message = f"""
                Hello {professional.get_full_name()},
                
                {instance.user.get_full_name()} has shared a journal entry with you dated {instance.date}.
                
                You can view it by logging into your account.
                
                Best regards,
                Mental Health Support Team
                """
                
                # Send email notification
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[professional.email],
                        fail_silently=True
                    )
                except Exception:
                    # Log this error but don't break the save process
                    pass



# Community Views
@login_required
def community_home(request):
    """Main community page showing categories and recent activity"""
    categories = Category.objects.filter(is_active=True)
    recent_threads = Thread.objects.filter(is_active=True).order_by('-created_at')[:5]
    pinned_threads = Thread.objects.filter(is_active=True, is_pinned=True)
    
    return render(request, 'Dashboards/community/home.html', {
        'categories': categories,
        'recent_threads': recent_threads,
        'pinned_threads': pinned_threads,
    })

class CategoryListView(ListView):
    """View for listing all forum categories"""
    model = Category
    template_name = 'Dashboards/community/forum/category_list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by('order')

class CategoryDetailView(DetailView):
    """View for displaying threads in a category"""
    model = Category
    template_name = 'Dashboards/community/forum/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        threads = Thread.objects.filter(category=self.object, is_active=True)
        
        # Filter threads based on search
        query = self.request.GET.get('q')
        if query:
            threads = threads.filter(Q(title__icontains=query) | Q(content__icontains=query))
        
        # Sort threads
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by not in ['-created_at', 'created_at', '-view_count', 'title']:
            sort_by = '-created_at'
        
        # Always keep pinned threads at top
        if sort_by != '-is_pinned':
            threads = threads.order_by('-is_pinned', sort_by)
        else:
            threads = threads.order_by(sort_by)
        
        # Paginate results
        paginator = Paginator(threads, 15)
        page = self.request.GET.get('page', 1)
        context['threads'] = paginator.get_page(page)
        context['thread_form'] = ThreadForm(initial={'category': self.object})
        
        return context

@method_decorator(login_required, name='dispatch')
class ThreadCreateView(CreateView):
    """View for creating a new thread"""
    model = Thread
    form_class = ThreadForm
    template_name = 'Dashboards/community/forum/thread_form.html'
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Thread created successfully!")
        return super().form_valid(form)
    
    def get_initial(self):
        initial = super().get_initial()
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            initial['category'] = category
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['category'] = get_object_or_404(Category, slug=category_slug)
        return context

class ThreadDetailView(DetailView):
    """View for displaying a thread and its comments"""
    model = Thread
    template_name = 'Dashboards/community/forum/thread_detail.html'
    context_object_name = 'thread'
    slug_url_kwarg = 'thread_slug'
    
    def get_object(self):
        category_slug = self.kwargs.get('category_slug')
        thread_slug = self.kwargs.get('thread_slug')
        thread = get_object_or_404(
            Thread, 
            slug=thread_slug, 
            category__slug=category_slug,
            is_active=True
        )
        # Increase view count if not author
        if self.request.user != thread.author:
            thread.increase_view_count()
        return thread
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(thread=self.object, parent=None, is_active=True)
        
        # Paginate comments
        paginator = Paginator(comments, 20)
        page = self.request.GET.get('page', 1)
        context['comments'] = paginator.get_page(page)
        context['comment_form'] = CommentForm()
        
        return context

@login_required
@require_POST
def thread_comment(request, category_slug, thread_slug):
    """View for adding a comment to a thread"""
    thread = get_object_or_404(Thread, slug=thread_slug, category__slug=category_slug, is_active=True)
    
    # Check if thread is locked
    if thread.is_locked:
        messages.error(request, "This thread is locked and cannot receive new comments.")
        return redirect(thread.get_absolute_url())
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.thread = thread
        comment.author = request.user
        
        # Check if it's a reply
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, id=parent_id, thread=thread)
        
        comment.save()
        messages.success(request, "Your comment has been posted.")
    else:
        messages.error(request, "There was an error posting your comment.")
    
    return redirect(thread.get_absolute_url())

@login_required
def thread_lock_toggle(request, category_slug, thread_slug):
    """View for locking/unlocking a thread"""
    thread = get_object_or_404(Thread, slug=thread_slug, category__slug=category_slug)
    
    # Check if user has permission
    if request.user != thread.author and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    thread.is_locked = not thread.is_locked
    thread.save()
    
    action = "locked" if thread.is_locked else "unlocked"
    messages.success(request, f"Thread has been {action}.")
    
    return redirect(thread.get_absolute_url())

@login_required
def thread_pin_toggle(request, category_slug, thread_slug):
    """View for pinning/unpinning a thread"""
    # Only staff can pin threads
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to perform this action.")
    
    thread = get_object_or_404(Thread, slug=thread_slug, category__slug=category_slug)
    thread.is_pinned = not thread.is_pinned
    thread.save()
    
    action = "pinned" if thread.is_pinned else "unpinned"
    messages.success(request, f"Thread has been {action}.")
    
    return redirect(thread.get_absolute_url())

# Anonymous Questions Views
@login_required
def anonymous_questions_list(request):
    """View for listing public anonymous questions"""
    questions = AnonymousQuestion.objects.filter(
        status='answered',
        is_public=True
    ).order_by('-created_at')
    
    # Search functionality
    query = request.GET.get('q')
    if query:
        questions = questions.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(response__icontains=query)
        )
    
    # Paginate results
    paginator = Paginator(questions, 10)
    page = request.GET.get('page', 1)
    
    return render(request, 'Dashboards/community/questions/anonymous_questions_list.html', {
        'questions': paginator.get_page(page),
        'question_form': AnonymousQuestionForm(),
    })

@login_required
def anonymous_question_create(request):
    """View for submitting an anonymous question"""
    if request.method == 'POST':
        form = AnonymousQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            # Store user reference for admin purposes but keep it anonymous to others
            question.asker = request.user
            question.save()
            messages.success(request, "Your question has been submitted anonymously and is awaiting response.")
            return redirect('anonymous_questions_list')
    else:
        form = AnonymousQuestionForm()
    
    return render(request, 'Dashboards/community/questions/anonymous_question_form.html', {
        'form': form
    })

@login_required
def my_anonymous_questions(request):
    """View for users to see their own anonymous questions"""
    questions = AnonymousQuestion.objects.filter(
        asker=request.user
    ).order_by('-created_at')
    
    return render(request, 'Dashboards/community/questions/my_anonymous_questions.html', {
        'questions': questions
    })

# Success Stories Views
class SuccessStoryListView(ListView):
    """View for listing success stories"""
    model = SuccessStory
    template_name = 'Dashboards/community/stories/success_story_list.html'
    context_object_name = 'stories'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = SuccessStory.objects.filter(is_approved=True)
        
        # Search functionality
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(author__last_name__icontains=query)
            )
        
        return queryset.order_by('-is_featured', '-created_at')

class SuccessStoryDetailView(DetailView):
    model = SuccessStory
    template_name = 'Dashboards/community/stories/success_story_detail.html'
    context_object_name = 'story'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        story = self.get_object()
        context['can_edit'] = self.request.user == story.author or self.request.user.is_staff
        context['can_delete'] = self.request.user == story.author or self.request.user.is_staff
        return context

@method_decorator(login_required, name='dispatch')
class SuccessStoryCreateView(LoginRequiredMixin, CreateView):
    model = SuccessStory
    form_class = SuccessStoryForm
    template_name = 'Dashboards/community/stories/success_story_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Your success story has been submitted and is awaiting approval.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('success_story_detail', kwargs={'slug': self.object.slug})

class SuccessStoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SuccessStory
    form_class = SuccessStoryForm
    template_name = 'Dashboards/community/stories/success_story_form.html'
    
    def test_func(self):
        story = self.get_object()
        return self.request.user == story.author or self.request.user.is_staff
    
    def form_valid(self, form):
        messages.success(self.request, "Your success story has been updated.")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('success_story_detail', kwargs={'slug': self.object.slug})

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        messages.error(self.request, "You don't have permission to edit this story.")
        return redirect('success_story_detail', slug=self.kwargs.get('slug'))

class SuccessStoryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SuccessStory
    template_name = 'Dashboards/community/stories/success_story_confirm_delete.html'
    context_object_name = 'story'
    
    def test_func(self):
        story = self.get_object()
        return self.request.user == story.author or self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Success story has been deleted.")
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('success_story_list')

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        messages.error(self.request, "You don't have permission to delete this story.")
        return redirect('success_story_detail', slug=self.kwargs.get('slug'))

# Mentorship Program Views
@login_required
def mentorship_programs_list(request):
    """View for listing available mentorship programs"""
    programs = MentorshipProgram.objects.filter(is_active=True)
    
    # Get user's current mentorship relationships
    if request.user.is_authenticated:
        mentor_relationships = MentorshipRelationship.objects.filter(
            mentor=request.user
        ).select_related('program', 'mentee')
        
        mentee_relationships = MentorshipRelationship.objects.filter(
            mentee=request.user
        ).select_related('program', 'mentor')
    else:
        mentor_relationships = MentorshipRelationship.objects.none()
        mentee_relationships = MentorshipRelationship.objects.none()
    
    return render(request, 'Dashboards/community/mentorship/mentorship_programs_list.html', {
        'programs': programs,
        'mentor_relationships': mentor_relationships,
        'mentee_relationships': mentee_relationships,
    })

@login_required
def mentorship_program_detail(request, pk):
    """View for displaying mentorship program details and applying"""
    program = get_object_or_404(MentorshipProgram, pk=pk, is_active=True)
    
    # Check if user is already in this program
    existing_relationship = MentorshipRelationship.objects.filter(
        Q(mentor=request.user) | Q(mentee=request.user),
        program=program
    ).first()
    
    if request.method == 'POST':
        form = MentorshipApplicationForm(request.POST)
        if form.is_valid():
            relationship = form.save(commit=False)
            relationship.program = program
            
            role = form.cleaned_data['role']
            if role == 'mentor':
                relationship.mentor = request.user
                # Admin will assign mentee later
            else:
                relationship.mentee = request.user
                # Admin will assign mentor later
            
            relationship.save()
            messages.success(request, "Your application has been submitted successfully!")
            return redirect('mentorship_programs_list')
    else:
        form = MentorshipApplicationForm()
    
    return render(request, 'Dashboards/community/mentorship/mentorship_program_detail.html', {
        'program': program,
        'form': form,
        'existing_relationship': existing_relationship,
    })

# Support Group Views
@login_required
def support_groups_list(request):
    """View for listing available support groups"""
    groups = SupportGroup.objects.filter(is_active=True)
    
    # Get user's current support groups
    if request.user.is_authenticated:
        user_groups = SupportGroupParticipant.objects.filter(
            user=request.user,
            status='approved'
        ).select_related('group')
    else:
        user_groups = SupportGroupParticipant.objects.none()
    
    # Get upcoming sessions
    upcoming_sessions = SupportGroupSession.objects.filter(
        is_completed=False,
        start_time__gt=timezone.now(),
        group__participants__user=request.user,
        group__participants__status='approved'
    ).order_by('start_time')[:5]
    
    return render(request, 'Dashboards/community/support/support_groups_list.html', {
        'groups': groups,
        'user_groups': user_groups,
        'upcoming_sessions': upcoming_sessions,
    })

@login_required
def support_group_detail_admin(request, pk):
    """View for displaying support group details and registering"""
    group = get_object_or_404(SupportGroup, pk=pk, is_active=True)
    
    # Check if user is already in this group
    try:
        participant = SupportGroupParticipant.objects.get(group=group, user=request.user)
    except SupportGroupParticipant.DoesNotExist:
        participant = None
    
    # Get upcoming sessions
    upcoming_sessions = SupportGroupSession.objects.filter(
        group=group,
        is_completed=False,
        start_time__gt=timezone.now()
    ).order_by('start_time')
    
    # Get past sessions
    past_sessions = SupportGroupSession.objects.filter(
        group=group,
        is_completed=True,
        start_time__lt=timezone.now()
    ).order_by('-start_time')
    
    # Get attendance records
    attendance_records = SupportGroupAttendance.objects.filter(
        session__group=group,
        participant__user=request.user
    ).select_related('session')
    
    # Get participant count
    participant_count = group.current_participant_count()
    
    # Check if group is full
    is_full = group.is_full()
    
    # Check if user is a facilitator
    is_facilitator = request.user == group.facilitator
    
    return render(request, 'Dashboards/community/support/support_group_detail.html', {
        'group': group,
        'participant': participant,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
        'attendance_records': attendance_records,
        'participant_count': participant_count,
        'is_full': is_full,
        'is_facilitator': is_facilitator,
    })



    # Continuing from where the code ended...

@login_required
def support_group_register(request, pk):
        """View for registering to a support group"""
        group = get_object_or_404(SupportGroup, pk=pk, is_active=True)
        
        # Check if group is full
        if group.is_full():
            messages.error(request, "This group is currently full. Please try another group or check back later.")
            return redirect('support_group_detail', pk=group.pk)
        
        # Check if user is already registered
        existing_registration = SupportGroupParticipant.objects.filter(group=group, user=request.user).first()
        if existing_registration:
            if existing_registration.status == 'pending':
                messages.info(request, "Your registration request is still pending approval.")
            elif existing_registration.status == 'approved':
                messages.info(request, "You are already a member of this group.")
            elif existing_registration.status == 'declined':
                messages.error(request, "Your previous registration was declined. Please contact the facilitator.")
            return redirect('support_group_detail', pk=group.pk)
        
        if request.method == 'POST':
            form = SupportGroupRegistrationForm(request.POST)
            if form.is_valid():
                participant = SupportGroupParticipant(
                    group=group,
                    user=request.user,
                    status='pending'
                )
                participant.save()
                
                # Notify facilitator (implementation depends on notification system)
                # ...
                
                messages.success(request, "Your registration request has been submitted and is awaiting approval.")
                return redirect('support_groups_list')
        else:
            form = SupportGroupRegistrationForm()
        
        return render(request, 'Dashboards/community/support/support_group_register.html', {
            'group': group,
            'form': form,
        })
    
@login_required
@require_POST
def support_group_leave(request, pk):
        """View for leaving a support group"""
        participant = get_object_or_404(
            SupportGroupParticipant, 
            group_id=pk, 
            user=request.user, 
            status='approved'
        )
        
        participant.status = 'left'
        participant.left_at = timezone.now()
        participant.save()
        
        messages.success(request, f"You have left the group '{participant.group.name}'.")
        return redirect('support_groups_list')
    
@login_required
def support_group_session_detail(request, group_pk, session_pk):
        """View for displaying session details and managing attendance"""
        session = get_object_or_404(
            SupportGroupSession,
            pk=session_pk,
            group_id=group_pk
        )
        group = session.group
        
        # Check if user is participant or facilitator
        is_facilitator = request.user == group.facilitator
        try:
            participant = SupportGroupParticipant.objects.get(
                group=group, 
                user=request.user,
                status='approved'
            )
            is_participant = True
        except SupportGroupParticipant.DoesNotExist:
            participant = None
            is_participant = False
        
        # Get or create attendance record if user is participant
        attendance = None
        if is_participant:
            attendance, created = SupportGroupAttendance.objects.get_or_create(
                session=session,
                participant=participant,
                defaults={'attended': False}
            )
        
        # Handle attendance confirmation
        if request.method == 'POST' and is_participant:
            action = request.POST.get('action')
            if action == 'confirm_attendance':
                attendance.attended = True
                attendance.save()
                messages.success(request, "Your attendance has been confirmed.")
            elif action == 'provide_feedback':
                feedback = request.POST.get('feedback')
                attendance.feedback = feedback
                attendance.save()
                messages.success(request, "Your feedback has been submitted.")
        
        # Get all attendance records if facilitator
        all_attendances = None
        if is_facilitator:
            all_attendances = SupportGroupAttendance.objects.filter(
                session=session
            ).select_related('participant', 'participant__user')
        
        return render(request, 'Dashboards/community/support_group_session_detail.html', {
            'session': session,
            'group': group,
            'is_facilitator': is_facilitator,
            'is_participant': is_participant,
            'attendance': attendance,
            'all_attendances': all_attendances,
        })
    
@login_required
@professional_required
def facilitated_groups(request):
        """View for professionals to manage their facilitated groups"""
        groups = SupportGroup.objects.filter(facilitator=request.user)
        
        # Get pending participation requests
        pending_requests = SupportGroupParticipant.objects.filter(
            group__facilitator=request.user,
            status='pending'
        ).select_related('group', 'user')
        
        # Get upcoming sessions to manage
        upcoming_sessions = SupportGroupSession.objects.filter(
            group__facilitator=request.user,
            is_completed=False,
            start_time__gt=timezone.now()
        ).order_by('start_time')
        
        return render(request, 'Dashboards/community/facilitated/facilitated_groups.html', {
            'groups': groups,
            'pending_requests': pending_requests,
            'upcoming_sessions': upcoming_sessions,
        })
    
@login_required
@professional_required
@require_POST
def participant_request_action(request, participant_id):
    """View for facilitators to approve/decline participant requests"""
    participant = get_object_or_404(
        SupportGroupParticipant,
        pk=participant_id,
        group__facilitator=request.user,
        status='pending'
    )
    
    action = request.POST.get('action')
    if action == 'approve':
        participant.status = 'approved'
        message = f"{participant.user.get_full_name()} has been approved to join the group."
        
        # Send approval email
        try:
            yag = yagmail.SMTP(settings.YAGMAIL_USER, settings.YAGMAIL_PASSWORD)
            subject = f"Approved: Your request to join {participant.group.name}"
            content = f"""
            <p>Dear {participant.user.get_full_name()},</p>
            
            <p>We're pleased to inform you that your request to join the support group 
            <strong>{participant.group.name}</strong> has been approved!</p>
            
            <p>Group details:</p>
            <ul>
                <li>Group Name: {participant.group.name}</li>
                <li>Facilitator: {participant.group.facilitator.get_full_name()}</li>
                <li>Frequency: {participant.group.get_frequency_display()}</li>
            </ul>
            
            <p>You can now access the group page and participate in upcoming sessions.</p>
            
            <p>Best regards,<br>
            The MentalApp Team</p>
            """
            yag.send(
                to=participant.user.email,
                subject=subject,
                contents=content
            )
        except Exception as e:
            # Log the error but don't show it to the user
            print(f"Failed to send approval email: {e}")
            
    elif action == 'decline':
        participant.status = 'declined'
        message = f"{participant.user.get_full_name()}'s request has been declined."
        
        # Send decline email
        try:
            yag = yagmail.SMTP(settings.YAGMAIL_USER, settings.YAGMAIL_PASSWORD)
            subject = f"Update: Your request to join {participant.group.name}"
            content = f"""
            <p>Dear {participant.user.get_full_name()},</p>
            
            <p>We regret to inform you that your request to join the support group 
            <strong>{participant.group.name}</strong> has not been approved at this time.</p>
            
            <p>This could be due to:</p>
            <ul>
                <li>The group being at full capacity</li>
                <li>Your needs not being the best match for this particular group</li>
            </ul>
            
            <p>We encourage you to explore other support groups in our community that might be a better fit.</p>
            
            <p>If you have any questions, please don't hesitate to contact us.</p>
            
            <p>Best regards,<br>
            The MentalApp Team</p>
            """
            yag.send(
                to=participant.user.email,
                subject=subject,
                contents=content
            )
        except Exception as e:
            # Log the error but don't show it to the user
            print(f"Failed to send decline email: {e}")
    else:
        messages.error(request, "Invalid action specified.")
        return redirect('facilitated_groups')
    
    participant.save()
    messages.success(request, message)
    return redirect('facilitated_groups')

### admin management forum

@method_decorator(staff_member_required, name='dispatch')
class CommunityAdminDashboard(TemplateView):
    template_name = 'Dashboards/community/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Forum statistics
        context['total_threads'] = Thread.objects.count()
        context['total_comments'] = Comment.objects.count()
        context['active_categories'] = Category.objects.filter(is_active=True).count()
        
        # Mentorship statistics
        context['active_programs'] = MentorshipProgram.objects.filter(is_active=True).count()
        context['active_relationships'] = MentorshipRelationship.objects.filter(
            status='active'
        ).count()
        
        # Support group statistics
        context['active_groups'] = SupportGroup.objects.filter(is_active=True).count()
        context['upcoming_sessions'] = SupportGroupSession.objects.filter(
            start_time__gt=timezone.now()
        ).count()
        
        # Recent activity
        context['recent_threads'] = Thread.objects.order_by('-created_at')[:5]
        context['recent_questions'] = AnonymousQuestion.objects.order_by('-created_at')[:5]
        context['recent_stories'] = SuccessStory.objects.order_by('-created_at')[:5]
        
        # Charts data
        context['category_thread_counts'] = Category.objects.annotate(
            thread_count=Count('threads')
        ).values('name', 'thread_count')
        
        return context

@method_decorator(staff_member_required, name='dispatch')
class ForumModerationView(ListView):
    template_name = 'Dashboards/community/admin/forum_moderation.html'
    model = Thread
    context_object_name = 'threads'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'reported':
            queryset = queryset.filter(reports__gt=0)
        elif status == 'locked':
            queryset = queryset.filter(is_locked=True)
        elif status == 'pinned':
            queryset = queryset.filter(is_pinned=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(content__icontains=search) |
                Q(author__username__icontains=search)
            )
        
        return queryset.order_by('-created_at')

@staff_member_required
def moderate_thread(request, thread_id):
    thread = Thread.objects.get(id=thread_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'lock':
            thread.is_locked = True
            thread.save()
            messages.success(request, f"Thread '{thread.title}' has been locked.")
        elif action == 'unlock':
            thread.is_locked = False
            thread.save()
            messages.success(request, f"Thread '{thread.title}' has been unlocked.")
        elif action == 'pin':
            thread.is_pinned = True
            thread.save()
            messages.success(request, f"Thread '{thread.title}' has been pinned.")
        elif action == 'unpin':
            thread.is_pinned = False
            thread.save()
            messages.success(request, f"Thread '{thread.title}' has been unpinned.")
        elif action == 'deactivate':
            thread.is_active = False
            thread.save()
            messages.success(request, f"Thread '{thread.title}' has been deactivated.")
        elif action == 'activate':
            thread.is_active = True
            thread.save()
            messages.success(request, f"Thread '{thread.title}' has been activated.")
        elif action == 'delete':
            thread.delete()
            messages.success(request, f"Thread '{thread.title}' has been deleted.")
        
        return redirect('forum_moderation')
    
    return render(request, 'Dashboards/community/admin/moderate_thread.html', {
        'thread': thread
    })

@method_decorator(staff_member_required, name='dispatch')
class MentorshipAdminView(ListView):
    template_name = 'Dashboards/community/admin/mentorship_admin.html'
    model = MentorshipProgram
    context_object_name = 'programs'
    
    def get_queryset(self):
        return MentorshipProgram.objects.annotate(
            relationship_count=Count('relationships')
        ).order_by('-is_active', '-start_date')
    

@staff_member_required
def mentorship_program_detail(request, program_id):
    program = MentorshipProgram.objects.get(id=program_id)
    relationships = program.relationships.select_related('mentor', 'mentee')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'activate':
            program.is_active = True
            program.save()
            messages.success(request, f"Program '{program.name}' has been activated.")
        elif action == 'deactivate':
            program.is_active = False
            program.save()
            messages.success(request, f"Program '{program.name}' has been deactivated.")
        
        return redirect('mentorship_admin')
    
    return render(request, 'Dashboards/community/admin/mentorship_program_detail.html', {
        'program': program,
        'relationships': relationships
    })

@method_decorator(staff_member_required, name='dispatch')
class SupportGroupAdminView(ListView):
    template_name = 'Dashboards/community/admin/support_group_admin.html'
    model = SupportGroup
    context_object_name = 'groups'
    
    def get_queryset(self):
        return SupportGroup.objects.annotate(
            participant_count=Count('participants')
        ).order_by('-is_active')

@staff_member_required
def support_group_detail(request, group_id):
    group = SupportGroup.objects.get(id=group_id)
    participants = SupportGroupParticipant.objects.filter(group=group).select_related('user')
    upcoming_sessions = SupportGroupSession.objects.filter(
        group=group,
        start_time__gt=timezone.now()
    ).order_by('start_time')
    past_sessions = SupportGroupSession.objects.filter(
        group=group,
        start_time__lte=timezone.now()
    ).order_by('-start_time')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'activate':
            group.is_active = True
            group.save()
            messages.success(request, f"Group '{group.name}' has been activated.")
        elif action == 'deactivate':
            group.is_active = False
            group.save()
            messages.success(request, f"Group '{group.name}' has been deactivated.")
        
        return redirect('support_group_admin')
    
    return render(request, 'Dashboards/community/admin/support_group_detail.html', {
        'group': group,
        'participants': participants,
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions
    })




# community/role_views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView

from .models import (
    SupportGroup, SupportGroupSession, SupportGroupParticipant,
    MentorshipProgram, MentorshipRelationship
)
from .forms import SupportGroupRegistrationForm

def is_coach(user):
    return hasattr(user, 'coach_profile')

def is_psychologist(user):
    return hasattr(user, 'psychologist_profile')

def is_nutritionist(user):
    return hasattr(user, 'nutritionist_profile')

@method_decorator([login_required, professional_required], name='dispatch')
class ProfessionalDashboard(TemplateView):
    template_name = 'Dashboards/community/professional/professional_dashboard.html'
    context_object_name = 'groups'
    
    def get_queryset(self):
        # Get groups where user is facilitator
        return SupportGroup.objects.filter(facilitator=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add mentorship programs for psychologists
        if is_psychologist(self.request.user):
            context['mentorship_programs'] = MentorshipProgram.objects.filter(is_active=True)
        return context

@login_required
@user_passes_test(lambda u: is_coach(u) or is_psychologist(u) or is_nutritionist(u))
def create_support_group(request):
    if request.method == 'POST':
        form = SupportGroupRegistrationForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.facilitator = request.user
            group.save()
            messages.success(request, "Support group created successfully!")
            return redirect('professional_dashboard')
    else:
        form = SupportGroupRegistrationForm()
    
    return render(request, 'Dashboards/community/professional/support_group_form.html', {
        'form': form,
        'title': 'Create Support Group'
    })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: is_psychologist(u)), name='dispatch')
class PsychologistMentorshipView(ListView):
    template_name = 'Dashboards/community/professional/psychologist_mentorship.html'
    model = MentorshipProgram
    context_object_name = 'programs'
    
    def get_queryset(self):
        return MentorshipProgram.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['relationships'] = MentorshipRelationship.objects.filter(
            mentor=self.request.user,
            status='active'
        )
        return context

@login_required
@user_passes_test(is_psychologist)
def respond_to_question(request, question_id):
    question = get_object_or_404(AnonymousQuestion, id=question_id, status='pending')
    
    if request.method == 'POST':
        response = request.POST.get('response')
        question.response = response
        question.respondent = request.user
        question.status = 'answered'
        question.save()
        messages.success(request, "Response submitted successfully!")
        return redirect('professional_dashboard')
    
    return render(request, 'Dashboards/community/professional/respond_to_question.html', {
        'question': question
    })



##chat
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Conversation, PrivateMessage, ClientAssignment
import jwt
from datetime import datetime, timedelta
from django.conf import settings

@login_required
def chat_home(request):
    """Main chat view with WebSocket token generation"""
    User = get_user_model()  # Get the User model here
    
    try:
        # Generate JWT token for WebSocket authentication
        token = jwt.encode({
            'user_id': str(request.user.id),
            'exp': datetime.utcnow() + timedelta(minutes=30)
        }, settings.SECRET_KEY, algorithm='HS256')

        conversations = Conversation.objects.filter(
            participants=request.user
        ).order_by('-updated_at').prefetch_related('participants', 'messages')
        
        # Annotate each conversation with unread count
        for conv in conversations:
            conv.unread_count = conv.messages.exclude(
                read_by=request.user
            ).exclude(
                sender=request.user
            ).count()
        
        active_conversation_id = request.GET.get('conversation')
        active_conversation = None
        if active_conversation_id:
            active_conversation = get_object_or_404(
                Conversation.objects.prefetch_related('messages__sender', 'messages__read_by'),
                id=active_conversation_id,
                participants=request.user
            )
            # Mark messages as read when opening conversation
            unread_messages = active_conversation.messages.exclude(sender=request.user).exclude(read_by=request.user)
            for message in unread_messages:
                message.read_by.add(request.user)

        context = {
            'conversations': conversations,
            'active_conversation': active_conversation,
            'available_users': get_available_users_for_chat(request.user),
            'websocket_token': token,
        }
        return render(request, 'Dashboards/Chat/chat_message.html', context)
    except Exception as e:
        print(f"Error in chat_home: {str(e)}")
        raise

    
def get_available_users_for_chat(user):
    """Get users that can be messaged based on user type"""
    User = get_user_model()  # Call it inside the function
    
    try:
        if not user.is_authenticated:
            return User.objects.none()
            
        base_query = User.objects.exclude(id=user.id).filter(is_active=True)
        
        if user.user_type == 'admin':
            return base_query.order_by('first_name')
        
        if user.user_type == 'athlete':
            return base_query.filter(
                assigned_clients__client=user,
                assigned_professionals__active=True
            ).order_by('first_name')
        
        if user.user_type in ['psychologist', 'coach', 'nutritionist']:
            return base_query.filter(
                Q(assigned_professionals__professional=user, assigned_professionals__active=True) |
                Q(user_type=user.user_type)
            ).distinct().order_by('first_name')
        
        return User.objects.none()
    except Exception as e:
        print(f"Error in get_available_users_for_chat: {str(e)}")
        return User.objects.none()

@login_required
def create_message(request):
    """HTTP endpoint for fallback message sending"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            conversation_id = data.get('conversation_id')
            content = data.get('content')
            
            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                participants=request.user
            )
            
            message = PrivateMessage.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            # Update conversation timestamp
            conversation.updated_at = timezone.now()
            conversation.save()
            
            return JsonResponse({
                'status': 'success',
                'message_id': str(message.id)
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)

@login_required
def new_conversation(request):
    """Create a new conversation with another user"""
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            other_user = get_object_or_404(User, id=user_id)
            
            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=other_user
            ).first()
            
            if existing_conversation:
                return JsonResponse({
                    'status': 'success',
                    'conversation_id': str(existing_conversation.id)
                })
            
            # Create new conversation
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user, other_user)
            
            return JsonResponse({
                'status': 'success',
                'conversation_id': str(conversation.id)
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)





@login_required
def AthleteCommunity(request):
    return render(request, 'Dashboards/Athlete/ Athlete Community/ AthleteCommunity.html')

@login_required
def ProgressTracker(request):
    return render(request, 'Dashboards/Athlete/ Progress Tracker/ ProgressTracker.html')



#Psychologist panel

@login_required
def PsychologistAssessments(request):
    """Psychologist view for assessments"""
    if request.user.user_type != 'psychologist':
        return HttpResponseForbidden("Access denied. Psychologist only.")
    
    # Get assessments created by this psychologist
    created_assessments = Assessment.objects.filter(creator=request.user)
    
    # Get assessments assigned by this psychologist
    assigned_assessments = AssignedAssessment.objects.filter(assigned_by=request.user)
    
    # Get responses that need review
    responses_to_review = AssessmentResponse.objects.filter(
        Q(assessment__creator=request.user) | Q(assignment__assigned_by=request.user),
        status='completed'
    ).exclude(psychologist_review__isnull=False)
    
    context = {
        'created_assessments': created_assessments,
        'assigned_assessments': assigned_assessments,
        'responses_to_review': responses_to_review,
        'can_create': True  # Add this flag
    }
    
    return render(request, 'Dashboards/Psychologist/Mental Assessments/Assessments.html', context)



@login_required
def PsychologistAppointments(request):
    return render(request, 'Dashboards/Psychologist/Appointments/Appointments.html')

@login_required
def PsychologistAthletes(request):
    return render(request, 'Dashboards/Psychologist/My Athletes/Athletes.html')

@login_required
def PsychologistWellnessResources(request):
    return render(request, 'Dashboards/Psychologist/Resources/Resources.html')

@login_required
def PsychologistCommunity(request):
    return render(request, 'Dashboards/Psychologist/Community/Community.html')

@login_required
def PsychologistSetting(request):
    return render(request, 'Dashboards/Psychologist/Setting/Setting.html')

# Coach panel



@login_required
def CoachForums(request):
    return render(request, 'Dashboards/Coach/Forums/Forums.html')

@login_required
def CoachMessages(request):
    return render(request, 'Dashboards/Coach/Messages/Messages.html')

@login_required
def CoachAthletes(request):
    return render(request, 'Dashboards/Coach/My Athletes/Athletes.html')

@login_required
def CoachResources(request):
    return render(request, 'Dashboards/Coach/Resources/Resources.html')

@login_required
def CoachSetting(request):
    return render(request, 'Dashboards/Coach/Setting/Setting.html')


#    Nutritionist panel
@login_required
def NutritionistAppointments(request):
    return render(request, 'Dashboards/Nutritionist/Appointments/Appointments.html')

@login_required
def NutritionistAthletes(request):  
    return render(request, 'Dashboards/Nutritionist/Athletes/Athletes.html')

@login_required
def NutritionistResources(request): 
    return render(request, 'Dashboards/Nutritionist/Resources/Resources.html')

@login_required
def NutritionistSetting(request):
    return render(request, 'Dashboards/Nutritionist/Setting/Setting.html')

@login_required
def NutritionistForum(request):
        return render(request, 'Dashboards/Nutritionist/Forum/Forum.html')





#athlete profile management

import uuid
import logging
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from campay.sdk import Client as CamPayClient
from io import BytesIO
from xhtml2pdf import pisa
from functools import wraps
from django.urls import reverse
from .forms import AthleteProfileForm
from .models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from .forms import AthleteProfileForm
from .models import User

# Set up logger
logger = logging.getLogger(__name__)

# Initialize CamPay client
campay_client = CamPayClient({
    "app_username": settings.CAMPAY_USERNAME,
    "app_password": settings.CAMPAY_PASSWORD,
    "environment": settings.CAMPAY_ENVIRONMENT  # "TEST" or "PROD"
})


# Now, create a profile completion check decorator

def profile_completion_required(view_func):
    """
    Decorator to check if an athlete's profile is complete.
    If not, redirects to the profile completion page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Only apply to athletes
        if request.user.is_authenticated and request.user.user_type == 'athlete':
            if not request.user.is_profile_complete():
                messages.warning(request, "Please complete your profile before accessing the dashboard.")
                return redirect('complete_athlete_profile')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Set up logger
logger = logging.getLogger(__name__)

@login_required
@transaction.atomic
def complete_athlete_profile(request):
    # Redirect if user is not an athlete
    if request.user.user_type != 'athlete':
        messages.error(request, "This page is only for athletes.")
        return redirect_to_dashboard(request.user)
    
    # Redirect if profile is already complete
    if request.user.is_profile_complete():
        messages.info(request, "Your profile is already complete.")
        return redirect('athlete_dashboard')
    
    if request.method == 'POST':
        form = AthleteProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            try:
                # Save form data without committing
                athlete = form.save(commit=False)
                
                # Save mobile number from form
                mobile_number = form.cleaned_data.get('mobile_number')
                if not mobile_number:
                    messages.error(request, "Mobile number is required for payment.")
                    return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {'form': form})
                
                # Format phone number (add country code if needed)
                if not mobile_number.startswith('237'):
                    mobile_number = '237' + mobile_number
                
                logger.info(f"Formatted mobile number: {mobile_number}")
                athlete.mobile_number = mobile_number
                athlete.terms_accepted = request.POST.get('terms') == 'on'
                
                # Ensure profile image was uploaded
                if 'profile_image' not in request.FILES:
                    messages.error(request, "Profile image is required.")
                    return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {'form': form})
                
                # Save the athlete to update fields
                athlete.save()
                
                # Generate payment reference
                payment_reference = str(uuid.uuid4())
                logger.info(f"Generated payment reference: {payment_reference}")
                
                # Initialize CamPay client
                campay_client = CamPayClient({
                    "app_username": settings.CAMPAY_USERNAME,
                    "app_password": settings.CAMPAY_PASSWORD,
                    "environment": settings.CAMPAY_ENVIRONMENT  # "TEST" or "PROD"
                })
                
                # Process payment with CamPay SDK
                # In the payment processing section of complete_athlete_profile view
                try:
                    payment_response = campay_client.collect({
                        "amount": str(int(athlete.membership_fee)),
                        "currency": "XAF",
                        "from": mobile_number,
                        "description": f"Athlete membership fee for {athlete.get_full_name()}",
                        "external_reference": payment_reference
                    })
                    
                    logger.info(f"Full payment response: {payment_response}")
                    
                    # Check if we got a proper response first
                    if not payment_response:
                        logger.error("Empty payment response received")
                        messages.error(request, "Payment system error: No response received")
                        return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {'form': form})
                    
                    # Handle UNAUTHORIZED error specifically
                    if isinstance(payment_response, dict) and payment_response.get('status') == 'FAILED' and payment_response.get('message') == 'UNAUTHORIZED':
                        logger.error(f"CamPay authentication failed: {payment_response}")
                        messages.error(request, "Payment system error: Authentication failed with the payment provider.")
                        # Record the failed payment attempt
                        athlete.payment_status = 'failed'
                        athlete.campay_status = 'FAILED'
                        athlete.campay_response = payment_response
                        athlete.save()
                        return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {'form': form})
                        
                    # Continue with normal reference checking
                    if not payment_response.get('reference'):
                        logger.error(f"Missing reference in payment response: {payment_response}")
                        messages.error(request, "Payment system error: No reference received")
                        return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {'form': form})
                    
                    # Record payment information
                    athlete.campay_reference = payment_response.get("reference")
                    athlete.campay_transaction_id = payment_response.get("reference")
                    athlete.campay_status = payment_response.get("status")
                    athlete.campay_response = payment_response
                    athlete.save()
                    
                    logger.info(f"Payment reference saved: {athlete.campay_reference}")
                    
                    if payment_response.get('status') == 'SUCCESSFUL':
                        # Update user status for successful payment
                        athlete.payment_status = 'paid'
                        athlete.last_payment_date = timezone.now()
                        athlete.next_payment_due = timezone.now() + timezone.timedelta(days=30)
                        athlete.account_status = 'active'
                        
                        # Generate receipt
                        receipt_filename, receipt_file = generate_pdf_receipt(athlete)
                        athlete.payment_receipt = ContentFile(receipt_file.getvalue(), name=receipt_filename)
                        
                        athlete.save()
                        
                        messages.success(request, "Profile completed successfully! Your payment has been processed.")
                        return redirect('athlete_dashboard')
                    else:
                        # Payment is pending or needs further action
                        athlete.payment_status = 'pending'
                        athlete.save()
                        
                        messages.info(request, "Your profile has been saved. Please complete the payment process on your mobile device.")
                        
                        # Make sure we're using the correct reference
                        payment_reference = payment_response.get("reference")
                        logger.info(f"Redirecting to payment status with reference: {payment_reference}")
                        return redirect('payment_status', reference=payment_reference)
                
                except Exception as e:
                    logger.error(f"Payment processing error: {str(e)}", exc_info=True)
                    messages.error(request, f"Payment processing failed: {str(e)}")
                    
                    # Record failed payment
                    athlete.payment_status = 'failed'
                    athlete.campay_status = 'FAILED'
                    athlete.campay_response = {'error': str(e)}
                    athlete.save()
                    return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {'form': form})
            
            except Exception as e:
                logger.error(f"Profile completion error: {str(e)}", exc_info=True)
                messages.error(request, f"Error while completing profile: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AthleteProfileForm(instance=request.user)
        # Pre-fill mobile number if available
        if request.user.mobile_number:
            form.initial['mobile_number'] = request.user.mobile_number
    
    # Get membership fee for display
    membership_fee = request.user.membership_fee
    
    return render(request, 'Dashboards/Athlete/CompleteProfile/complete_profile.html', {
        'form': form,
        'membership_fee': membership_fee
    })

# Apply decorator to athlete_dashboard
@login_required
@profile_completion_required
def athlete_dashboard(request):
    return render(request, 'Dashboards/Athlete/AthletePanel.html')

# Add a new view to check profile completion status
@login_required
def check_profile_completion(request):
    """API endpoint to check if user profile is complete"""
    if request.user.is_authenticated:
        is_complete = request.user.is_profile_complete()
        return JsonResponse({
            'is_complete': is_complete,
            'redirect_url': reverse('complete_athlete_profile') if not is_complete else None
        })
    return JsonResponse({'error': 'Authentication required'}, status=401)

# Update the User model's is_profile_complete method to be more robust
def is_profile_complete(self):
    """Check if the user has completed their profile based on their user type"""
    if self.user_type == 'athlete':
        required_fields = [
            self.first_name, 
            self.last_name, 
            self.email,
            self.sport,
            self.level,
            self.town,
            self.quartier,
            self.profile_image,
            self.payment_status == 'paid'  # Added payment check
        ]
        return all(required_fields)
    elif self.user_type in ['psychologist', 'coach', 'nutritionist']:
        required_fields = [
            self.first_name, 
            self.last_name, 
            self.email,
            self.qualifications,
            self.years_experience,
            self.town,
            self.profile_image,
            self.certification_document,
            self.cv_document,
            self.payment_status == 'paid'  # Added payment check
        ]
        return all(required_fields)
    return True  # Admins don't need complete profiles

@login_required
def payment_status(request, reference):
    """View to check and display payment status"""
    try:
        # Get user's transaction
        user = request.user
        
        if not user.campay_reference or user.campay_reference != reference:
            messages.error(request, "Invalid payment reference.")
            return redirect('athlete_dashboard')
        
        # Check payment status with CamPay
        try:
            # Use the correct method name - most likely 'status' or 'get_status'
            status_response = campay_client.status(reference)
            # OR if the method is get_status
            # status_response = campay_client.get_status(reference)
            
            logger.info(f"Payment status response: {status_response}")
            
            # Update payment information
            user.campay_status = status_response.get("status")
            user.campay_response = status_response
            
            if status_response.get('status') == 'SUCCESSFUL':
                # Update user status for successful payment
                user.payment_status = 'paid'
                user.last_payment_date = timezone.now()
                user.next_payment_due = timezone.now() + timezone.timedelta(days=30)
                user.account_status = 'active'
                
                # Generate receipt
                receipt_filename, receipt_file = generate_pdf_receipt(user)
                user.payment_receipt = ContentFile(receipt_file.getvalue(), name=receipt_filename)
                
                user.save()
                
                messages.success(request, "Payment successful! Your profile is now complete.")
                return redirect('athlete_dashboard')
            else:
                # Payment is still pending or failed
                status = status_response.get('status', 'UNKNOWN').upper()
                if status == 'FAILED':
                    user.payment_status = 'failed'
                    messages.error(request, "Payment failed. Please try again.")
                else:
                    user.payment_status = 'pending'
                    messages.info(request, "Your payment is still processing. Please check back later.")
                
                user.save()
        
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")
            messages.error(request, f"Error checking payment status: {str(e)}")
            
    except Exception as e:
        logger.error(f"Payment status view error: {str(e)}")
        messages.error(request, "An error occurred while checking your payment status.")
    
    return render(request, 'Dashboards/Athlete/CompleteProfile/PaymentStatus.html', {
        'reference': reference,
        'status': user.campay_status,
        'payment_date': user.last_payment_date
    })


def generate_pdf_receipt(user):
    """Generate a PDF receipt for the user's payment"""
    try:
        # Context data for the receipt template
        context = {
            'user': user,
            'payment_date': user.last_payment_date or timezone.now(),
            'amount': user.membership_fee,
            'reference': user.campay_reference,
            'transaction_id': user.campay_transaction_id,
            'next_payment_date': user.next_payment_due,
            'generated_date': timezone.now(),
            'receipt_number': f"REC-{timezone.now().strftime('%Y%m%d')}-{user.id}"
        }
        
        # Render the receipt template
        html_string = render_to_string('Dashboards/Athlete/Receipts/MembershipReceipt.html', context)
        
        # Create a PDF file
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            # Generate a unique filename
            filename = f"membership_receipt_{user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            return filename, result
        else:
            logger.error(f"Error generating PDF receipt: {pdf.err}")
            raise Exception("Error generating PDF receipt")
    except Exception as e:
        logger.error(f"Error in generate_pdf_receipt: {str(e)}")
        raise

@login_required
def download_receipt(request):
    """View to download the user's payment receipt"""
    user = request.user
    
    if not hasattr(user, 'payment_receipt') or not user.payment_receipt:
        messages.error(request, "No receipt available. Please complete your payment first.")
        return redirect('athlete_dashboard')
    
    try:
        # Get the file path
        file_path = user.payment_receipt.path
        
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                response = HttpResponse(f, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
        else:
            messages.error(request, "Receipt file not found.")
            return redirect('athlete_dashboard')
    except Exception as e:
        logger.error(f"Error downloading receipt: {str(e)}")
        messages.error(request, f"Error downloading receipt: {str(e)}")
        return redirect('athlete_dashboard')




    