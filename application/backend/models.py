from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db import migrations, models
import django.db.models.deletion
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings
from backend.scoring import ScoreCalculator
from .scoring import ScoreCalculator
from django.utils.text import slugify
import uuid
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email
    
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('athlete', 'Athlete'),
        ('psychologist', 'Psychologist'),
        ('coach', 'Mental Coach'),
        ('nutritionist', 'Nutritionist'),
        ('admin', 'Administrator'),
    )
    
    SPORT_CHOICES = (
        ('boxing', 'Boxing'),
        ('wrestling', 'Wrestling'),
        ('judo', 'Judo'),
        ('karate', 'Karate'),
        ('taekwondo', 'Taekwondo'),
        ('mma', 'Mixed Martial Arts'),
        ('other', 'Other'),
    )
    
    LEVEL_CHOICES = (
        ('amateur', 'Amateur'),
        ('semi-pro', 'Semi-Professional'),
        ('professional', 'Professional'),
        ('elite', 'Elite'),
    )
    
    ACCOUNT_STATUS_CHOICES = (
        ('pending', 'Pending Verification'),
        ('active', 'Active'),
        ('blocked', 'Blocked'),
        ('suspended', 'Temporarily Suspended'),
    )
    
    # Basic profile fields
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='athlete')
    sport = models.CharField(max_length=20, choices=SPORT_CHOICES, blank=True, null=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True, null=True)
    qualifications = models.CharField(max_length=255, blank=True, null=True)
    years_experience = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(50)]
    )
    
    # Profile fields
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    town = models.CharField(max_length=100, blank=True, null=True)
    quartier = models.CharField(max_length=100, blank=True, null=True)
    account_status = models.CharField(
        max_length=20, 
        choices=ACCOUNT_STATUS_CHOICES, 
        default='pending'
    )
    
    # Professional verification fields
    is_verified_professional = models.BooleanField(default=False)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    certification_document = models.FileField(
        upload_to='certification_documents/', 
        blank=True, 
        null=True,
        help_text='Upload your professional certification or license'
    )
    cv_document = models.FileField(
        upload_to='cv_documents/', 
        blank=True, 
        null=True,
        help_text='Upload your professional CV or resume'
    )
    additional_documents = models.FileField(
        upload_to='additional_documents/', 
        blank=True, 
        null=True,
        help_text='Upload any additional supporting documents'
    )
    verification_notes = models.TextField(blank=True, null=True)
    
    # Payment related fields
    membership_fee = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0.00,
        help_text='Monthly membership fee based on user type'
    )
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    last_payment_date = models.DateTimeField(blank=True, null=True)
    next_payment_due = models.DateTimeField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('expired', 'Expired'),
        ),
        default='pending'
    )
    
    # Campay specific fields
    campay_reference = models.CharField(max_length=255, blank=True, null=True)
    campay_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    campay_status = models.CharField(max_length=50, blank=True, null=True)
    campay_response = models.JSONField(blank=True, null=True)
    
    # Receipt field
    payment_receipt = models.FileField(
        upload_to='receipts/',
        blank=True,
        null=True,
        help_text='PDF receipt for membership payment'
    )
    # Other fields
    terms_accepted = models.BooleanField(default=False)
    social_provider = models.CharField(max_length=20, blank=True, null=True)
    social_uid = models.CharField(max_length=200, blank=True, null=True)
    date_verified = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Set default membership fees based on user type
        if not self.pk or self.membership_fee == 0.00:  # Only set on creation or if not manually set
            if self.user_type == 'athlete':
                self.membership_fee = 05.00  # CFA
            elif self.user_type == 'psychologist':
                self.membership_fee = 07.00  # CFA
            elif self.user_type == 'coach':
                self.membership_fee = 08.00  # CFA
            elif self.user_type == 'nutritionist':
                self.membership_fee = 10.00  # CFA
            elif self.user_type == 'admin':
                self.membership_fee = 0.00
        super().save(*args, **kwargs)
    
    def is_profile_complete(self):
        """Check if the user has completed their profile based on their user type"""
        if self.user_type == 'athlete':
            return all([
                self.first_name, 
                self.last_name, 
                self.email,
                self.sport,
                self.level,
                self.town,
                self.profile_image,
                self.payment_status == 'paid'  # Added payment check
            ])
        elif self.user_type in ['psychologist', 'coach', 'nutritionist']:
            return all([
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
            ])
        return True  # Admins don't need complete profiles
    
    def record_payment(self, reference, transaction_id=None, status=None, response_data=None):
        """Record a payment attempt with Campay"""
        self.campay_reference = reference
        if transaction_id:
            self.campay_transaction_id = transaction_id
        if status:
            self.campay_status = status
            
            # Update payment status based on Campay status
            if status.lower() in ['success', 'successful', 'completed']:
                self.payment_status = 'paid'
                self.last_payment_date = timezone.now()
                self.next_payment_due = timezone.now() + timezone.timedelta(days=30)
            elif status.lower() in ['failed', 'rejected', 'cancelled']:
                self.payment_status = 'failed'
        
        if response_data:
            self.campay_response = response_data
            
        self.save()
    
    def is_subscription_active(self):
        """Check if user's subscription is active"""
        if self.payment_status != 'paid':
            return False
        
        if not self.next_payment_due:
            return False
            
        return timezone.now() < self.next_payment_due
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0XXX_previous_migration'),  # Replace with your latest migration
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('verification_code', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_used', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.User')),
            ],
        ),
    ]

class SpecialistProfile(models.Model):
    """Extended profile information for specialists"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='specialist_profile')
    bio = models.TextField(help_text="Professional biography")
    expertise_areas = models.TextField(help_text="Areas of expertise or specialization")
    education = models.TextField(help_text="Educational background")
    languages = models.CharField(max_length=255, help_text="Languages spoken")
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, help_text="Hourly consultation rate")
    session_duration_options = models.CharField(
        max_length=255,
        default="30,45,60,90",
        help_text="Available session durations in minutes (comma separated values)"
    )
    availability = models.JSONField(
        default=dict,
        help_text="JSON representing weekly availability schedule"
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Average rating from 0 to 5"
    )
    review_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"
    
    def get_available_session_durations(self):
        """Returns list of available session durations"""
        return [int(duration) for duration in self.session_duration_options.split(",")]

class AppointmentRequest(models.Model):
    """Model to handle appointment requests from athletes to specialists"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('canceled', 'Canceled'),
        ('completed', 'Completed'),
    )
    
    athlete = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='requested_appointments'
    )
    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='received_appointments'
    )
    date = models.DateField()
    time = models.TimeField()
    duration = models.PositiveIntegerField(
        default=60,
        help_text="Duration in minutes",
        validators=[MinValueValidator(15), MaxValueValidator(180)]
    )
    reason = models.TextField(help_text="Reason for the appointment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    response_message = models.TextField(
        blank=True, 
        null=True, 
        help_text="Specialist's response to the appointment request"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Add video session fields
     # Update video session fields
    jitsi_room_id = models.CharField(max_length=255, blank=True, null=True)
    jitsi_room_password = models.CharField(max_length=64, blank=True, null=True)
    jitsi_room_created = models.BooleanField(default=False)
    
    def generate_jitsi_room_details(self):
        """Generate a unique room ID and password for Jitsi"""
        import uuid
        import random
        import string
        
        if not self.jitsi_room_id:
            # Create a unique room ID based on appointment ID and a UUID
            self.jitsi_room_id = f"athletic-session-{self.id}-{uuid.uuid4().hex[:8]}"
            
            # Generate a secure password
            chars = string.ascii_letters + string.digits
            self.jitsi_room_password = ''.join(random.choice(chars) for _ in range(12))
            self.jitsi_room_created = True
            self.save()
        
        return {
            'room_id': self.jitsi_room_id,
            'password': self.jitsi_room_password
        }


class AppointmentReview(models.Model):
    """Model for reviews after completed appointments"""
    appointment = models.OneToOneField(AppointmentRequest, on_delete=models.CASCADE, related_name='review')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField(help_text="Review comment")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Update specialist's rating when review is saved"""
        super().save(*args, **kwargs)
        
        # Update specialist's rating
        specialist = self.appointment.specialist
        try:
            profile = specialist.specialist_profile
            profile.review_count += 1
            
            # Calculate new average rating
            all_reviews = AppointmentReview.objects.filter(
                appointment__specialist=specialist
            )
            total_rating = sum(review.rating for review in all_reviews)
            profile.rating = total_rating / profile.review_count
            profile.save()
        except SpecialistProfile.DoesNotExist:
            pass

class AppointmentNote(models.Model):
    """Private notes for appointments"""
    appointment = models.ForeignKey(AppointmentRequest, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=True, help_text="Whether this note is private to the author")
    
    def __str__(self):
        return f"Note for {self.appointment} by {self.author.get_full_name()}"

class AssessmentCategory(models.Model):
    """Categories for different types of mental assessments"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, null=True)  # For UI representation
    
    def __str__(self):
        return self.name

class Assessment(models.Model):
    """Model for assessment questionnaires"""
    DIFFICULTY_CHOICES = (
        ('basic', 'Basic'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(AssessmentCategory, on_delete=models.CASCADE, related_name='assessments')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type__in': ['psychologist', 'admin']})
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='intermediate')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False, help_text="Whether this assessment is available to all athletes")
    estimated_time_minutes = models.PositiveIntegerField(default=15)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Assessment configuration
    show_results_immediately = models.BooleanField(default=True)
    require_psychologist_review = models.BooleanField(default=False)
    allow_retake = models.BooleanField(default=True)
    minimum_days_between_retakes = models.PositiveIntegerField(default=7, help_text="Minimum days required between retakes")
    
    def __str__(self):
        return self.title
    
    def is_available_for_user(self, user):
        """Check if assessment is available for a specific user"""
        if not self.is_public and self.creator != user:
            # For private assessments, check if specifically assigned
            return AssignedAssessment.objects.filter(assessment=self, athlete=user).exists()
        return self.status == 'published'

class Question(models.Model):
    """Individual questions within an assessment"""
    QUESTION_TYPES = (
        ('likert_5', '5-point Likert Scale'),
        ('likert_7', '7-point Likert Scale'),
        ('yes_no', 'Yes/No'),
        ('multiple_choice', 'Multiple Choice'),
        ('slider', 'Slider'),
        ('text', 'Open Text'),
    )
    
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    help_text = models.TextField(blank=True, null=True)
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # Fields for scoring
    reverse_scoring = models.BooleanField(default=False, help_text="Whether this question should be reverse-scored")
    weight = models.FloatField(default=1.0, help_text="Weight of this question in the overall score")
    
    # For multiple-choice questions
    choices = models.JSONField(null=True, blank=True, help_text="JSON array of choices for multiple choice questions")
    
    # For slider questions
    min_value = models.IntegerField(null=True, blank=True)
    max_value = models.IntegerField(null=True, blank=True)
    step = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.assessment.title} - Q{self.order}: {self.text[:50]}..."

class ResponseScale(models.Model):
    """Definition of scales and interpretation ranges for assessments"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scales')
    name = models.CharField(max_length=100)
    description = models.TextField()
    min_score = models.FloatField()
    max_score = models.FloatField()
    
    # Define ranges for interpretation
    ranges = models.JSONField(help_text="JSON array of interpretation ranges with labels")
    
    def __str__(self):
        return f"{self.assessment.title} - {self.name} Scale"
    
    def interpret_score(self, score):
        """Interpret a score based on defined ranges"""
        for range_def in self.ranges:
            if range_def['min'] <= score <= range_def['max']:
                return {
                    'label': range_def['label'],
                    'description': range_def['description'],
                    'recommendations': range_def.get('recommendations', []),
                    'color': range_def.get('color', '#3498db')  # Default color
                }
        return None

class AssignedAssessment(models.Model):
    """Assessments assigned to specific athletes by psychologists"""
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_assessments', limit_choices_to={'user_type': 'athlete'})
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments_given', limit_choices_to={'user_type': 'psychologist'})
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    instructions = models.TextField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.assessment.title} assigned to {self.athlete.get_full_name()}"

class AssessmentResponse(models.Model):
    """Record of an athlete's complete response to an assessment"""
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed by Psychologist'),
    )
    
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='responses')
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_responses', limit_choices_to={'user_type': 'athlete'})
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    # If this response is from an assigned assessment
    assignment = models.ForeignKey(AssignedAssessment, on_delete=models.SET_NULL, null=True, blank=True, related_name='responses')
    
    # Calculated scores for each scale
    scores = models.JSONField(null=True, blank=True)
    
    # Additional metrics
    completion_time_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.athlete.get_full_name()} - {self.assessment.title} ({self.started_at.strftime('%Y-%m-%d')})"
    
    def calculate_scores(self):
        """Calculate scores for this response based on answers"""
        from .scoring import ScoreCalculator
        
        calculator = ScoreCalculator(self)
        self.scores = calculator.calculate()
        
        if self.status == 'in_progress':
            self.status = 'completed'
            self.completed_at = timezone.now()
            
            # Calculate completion time
            time_diff = self.completed_at - self.started_at
            self.completion_time_seconds = int(time_diff.total_seconds())
            
            # Mark assignment as completed if applicable
            if self.assignment:
                self.assignment.completed = True
                self.assignment.save()
                
        self.save()
        
        return self.scores

class QuestionResponse(models.Model):
    """Individual responses to questions"""
    assessment_response = models.ForeignKey(AssessmentResponse, on_delete=models.CASCADE, related_name='question_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_value = models.JSONField(help_text="JSON value of the answer (format depends on question type)")
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['assessment_response', 'question']
    
    def __str__(self):
        return f"Response to {self.question.text[:30]}..."

class PsychologistReview(models.Model):
    """Professional review of an assessment response"""
    assessment_response = models.OneToOneField(AssessmentResponse, on_delete=models.CASCADE, related_name='psychologist_review')
    psychologist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assessment_reviews', limit_choices_to={'user_type': 'psychologist'})
    review_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField()
    recommendations = models.TextField()
    follow_up_needed = models.BooleanField(default=False)
    
    # Custom score adjustments (if psychologist disagrees with automated scoring)
    score_adjustments = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"Review of {self.assessment_response}"

class RecommendedSpecialist(models.Model):
    """Specialists recommended based on assessment results"""
    assessment_response = models.ForeignKey(AssessmentResponse, on_delete=models.CASCADE, related_name='recommended_specialists')
    specialist = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='specialist_recommendations', limit_choices_to={'user_type__in': ['psychologist', 'coach', 'nutritionist']})
    recommendation_reason = models.TextField()
    priority = models.PositiveIntegerField(default=1, help_text="Priority level (1 = highest)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['priority']
    
    def __str__(self):
        return f"{self.specialist.get_full_name()} recommended for {self.assessment_response.athlete.get_full_name()}"

class ProgressMetric(models.Model):
    """Tracking metrics for measuring mental health progress over time"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    assessment_category = models.ForeignKey(AssessmentCategory, on_delete=models.CASCADE, related_name='metrics')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'user_type__in': ['psychologist', 'admin']})
    min_value = models.FloatField()
    max_value = models.FloatField()
    default_goal = models.FloatField(null=True, blank=True)
    higher_is_better = models.BooleanField(default=True, help_text="Whether higher values represent improvement")
    
    def __str__(self):
        return self.name

class AthleteMetricProgress(models.Model):
    """Record of an athlete's progress on specific metrics over time"""
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='metric_progress', limit_choices_to={'user_type': 'athlete'})
    metric = models.ForeignKey(ProgressMetric, on_delete=models.CASCADE, related_name='athlete_progress')
    value = models.FloatField()
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    assessment_response = models.ForeignKey(AssessmentResponse, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_metrics')
    
    class Meta:
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.athlete.get_full_name()} - {self.metric.name}: {self.value} on {self.date}"

class ResourceCategory(models.Model):
    """Categories for wellness resources"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For UI representation
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = "Resource Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class WellnessResource(models.Model):
    """Self-help resources for athletes"""
    CONTENT_TYPE_CHOICES = (
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('pdf', 'PDF Document'),
        ('exercise', 'Interactive Exercise'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(ResourceCategory, on_delete=models.CASCADE, related_name='resources')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    description = models.TextField()
    content = models.TextField(blank=True, null=True, help_text="HTML content for articles")
    external_url = models.URLField(blank=True, null=True, help_text="URL for external content like videos")
    file = models.FileField(upload_to='wellness_resources/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='resource_thumbnails/', blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_resources')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    
    # Tagging
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    
    # Related resources
    related_resources = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def increment_view_count(self):
        self.view_count += 1
        self.save()
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class SavedResource(models.Model):
    """Resources saved/bookmarked by athletes"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_resources')
    resource = models.ForeignKey(WellnessResource, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="User's notes about this resource")
    
    class Meta:
        unique_together = ['user', 'resource']
        ordering = ['-saved_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"

class ResourceRating(models.Model):
    """Ratings for resources"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resource_ratings')
    resource = models.ForeignKey(WellnessResource, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    review = models.TextField(null=True, blank=True)

    
    class Meta:
        unique_together = ['user', 'resource']
    
    def __str__(self):
        return f"{self.user.username} rated {self.resource.title}: {self.rating}"

class JournalEntry(models.Model):
    """Mental health journal entries for athletes"""
    MOOD_CHOICES = (
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('neutral', 'Neutral'),
        ('bad', 'Bad'),
        ('terrible', 'Terrible'),
    )
    
    ENERGY_LEVEL_CHOICES = (
        ('very_high', 'Very High'),
        ('high', 'High'),
        ('moderate', 'Moderate'),
        ('low', 'Low'),
        ('very_low', 'Very Low'),
    )
    
    STRESS_LEVEL_CHOICES = (
        ('none', 'None'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('severe', 'Severe'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries')
    date = models.DateField()
    title = models.CharField(max_length=200, blank=True, null=True)
    content = models.TextField()
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    energy_level = models.CharField(max_length=20, choices=ENERGY_LEVEL_CHOICES, blank=True, null=True)
    stress_level = models.CharField(max_length=20, choices=STRESS_LEVEL_CHOICES, blank=True, null=True)
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags")
    
    # Sharing options
    is_private = models.BooleanField(default=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='shared_journal_entries',
        blank=True,
        limit_choices_to={'user_type__in': ['psychologist', 'coach']}
    )
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name_plural = "Journal Entries"
        unique_together = ['user', 'date']  # One main entry per day
    
    def __str__(self):
        return f"{self.user.username} - {self.date}: {self.title or 'Journal Entry'}"
    
    def get_tags_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class JournalPrompt(models.Model):
    """Prompts to help athletes with journaling"""
    text = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_prompts')
    is_active = models.BooleanField(default=True)

    
    def __str__(self):
        return self.text[:50] + ('...' if len(self.text) > 50 else '')

class JournalTemplate(models.Model):
    """Templates for structured journal entries"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    structure = models.JSONField(help_text="JSON structure defining the template fields")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_templates')
    is_public = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

## Forum

class Category(models.Model):
    """Forum category model for organizing discussions by topic/sport"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True, help_text="CSS icon class name")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    
    def thread_count(self):
        return Thread.objects.filter(category=self, is_active=True).count()

class Thread(models.Model):
    """Thread model for starting discussions within categories"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='threads')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='threads')
    content = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            similar_slugs = Thread.objects.filter(slug__startswith=self.slug).count()
            if similar_slugs > 0:
                self.slug = f"{self.slug}-{similar_slugs}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('thread_detail', kwargs={'category_slug': self.category.slug, 'thread_slug': self.slug})
    
    def comment_count(self):
        return Comment.objects.filter(thread=self, is_active=True).count()
    
    def last_activity(self):
        last_comment = self.comments.filter(is_active=True).order_by('-created_at').first()
        if last_comment:
            return last_comment.created_at
        return self.created_at
    
    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

class Comment(models.Model):
    """Comment model for replies in threads"""
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.get_username()} on {self.thread.title}"
    
    def get_absolute_url(self):
        return f"{self.thread.get_absolute_url()}#comment-{self.id}"

class MentorshipProgram(models.Model):
    """Mentorship program model for matching mentors with mentees"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name
    
    def is_open_for_registration(self):
        today = timezone.now().date()
        if self.end_date:
            return self.is_active and self.start_date <= today <= self.end_date
        return self.is_active and self.start_date <= today

class MentorshipRelationship(models.Model):
    """Model for relationships between mentors and mentees"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    program = models.ForeignKey(MentorshipProgram, on_delete=models.CASCADE, related_name='relationships')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mentoring')
    mentee = models.ForeignKey(
            settings.AUTH_USER_MODEL, 
            on_delete=models.CASCADE, 
            related_name='mentored',
            null=True,  # Add this
            blank=True  # Add this
        )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    goals = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('program', 'mentor', 'mentee')
    
    def __str__(self):
        return f"{self.mentor.get_full_name()} mentoring {self.mentee.get_full_name()}"

class AnonymousQuestion(models.Model):
    """Model for anonymous questions from users"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('answered', 'Answered'),
        ('rejected', 'Rejected'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    asker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='anonymous_questions')
    respondent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='answered_questions')
    response = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class SuccessStory(models.Model):
    """Model for athlete success stories"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=False)  # Temporarily non-unique
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='success_stories')
    content = models.TextField()
    featured_image = models.ImageField(upload_to='success_stories/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_anonymous = models.BooleanField(default=False)

    
    class Meta:
        verbose_name_plural = "Success stories"
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            similar_slugs = SuccessStory.objects.filter(slug__startswith=self.slug).count()
            if similar_slugs > 0:
                self.slug = f"{self.slug}-{similar_slugs}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('success_story_detail', kwargs={'slug': self.slug})
    
    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:4]}")
        super().save(*args, **kwargs)

    def can_edit(self, user):
        return user == self.author or user.is_staff
    
    def can_delete(self, user):
        return user == self.author or user.is_staff

class SupportGroup(models.Model):
    """Model for virtual support groups"""
    FREQUENCY_CHOICES = (
        ('one-time', 'One-time Session'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    facilitator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='facilitated_groups')
    max_participants = models.PositiveIntegerField(default=10)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    meeting_link = models.URLField(blank=True, null=True)
    meeting_password = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the participant")

    
    def __str__(self):
        return self.name
    
    def current_participant_count(self):
        return self.participants.count()
    
    def is_full(self):
        return self.current_participant_count() >= self.max_participants

class SupportGroupSession(models.Model):
    """Model for individual sessions of support groups"""
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_link = models.URLField(blank=True, null=True)
    meeting_password = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_time']
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Use group's meeting link/password if not specified
        if not self.meeting_link and self.group.meeting_link:
            self.meeting_link = self.group.meeting_link
        if not self.meeting_password and self.group.meeting_password:
            self.meeting_password = self.group.meeting_password
        super().save(*args, **kwargs)
    
    def is_upcoming(self):
        return self.start_time > timezone.now()
    
    def is_in_progress(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time

class SupportGroupParticipant(models.Model):
    """Model for participants in support groups"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
        ('left', 'Left Group'),
    )
    
    group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_groups')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)  # Add this line

    
    class Meta:
        unique_together = ('group', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.group.name}"

class SupportGroupAttendance(models.Model):
    """Model for tracking attendance in support group sessions"""
    session = models.ForeignKey(SupportGroupSession, on_delete=models.CASCADE, related_name='attendances')
    participant = models.ForeignKey(SupportGroupParticipant, on_delete=models.CASCADE, related_name='attendances')
    attended = models.BooleanField(default=False)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('session', 'participant')
    
    def __str__(self):
        status = "Attended" if self.attended else "Did not attend"
        return f"{self.participant.user.get_full_name()} - {status} - {self.session.title}"




## chat web stocket

from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
import os
import uuid
from django.core.validators import FileExtensionValidator, MaxValueValidator

# Import the User model which already exists
User = settings.AUTH_USER_MODEL

def message_file_path(instance, filename):
    """Generate file path for uploaded message files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('message_files', filename)

def forum_file_path(instance, filename):
    """Generate file path for uploaded forum files"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('forum_files', filename)

class ClientAssignment(models.Model):
    """Model to track professional-client relationships"""
    professional = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='assigned_clients'
    )
    client = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='assigned_professionals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('professional', 'client')

    def __str__(self):
        return f"{self.professional.get_full_name()} - {self.client.get_full_name()}"


class Conversation(models.Model):
    """Model to represent a private conversation between users"""
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # For encryption
    encryption_key = models.CharField(max_length=64, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Generate encryption key if not already set
        if not self.encryption_key:
            self.encryption_key = get_random_string(64)
        super().save(*args, **kwargs)
    
    def is_participant(self, user):
        """Check if a user is part of this conversation"""
        return self.participants.filter(id=user.id).exists()
    
    def add_message(self, sender, content, file=None):
        """Helper method to add a message to the conversation"""
        message = PrivateMessage.objects.create(
            conversation=self,
            sender=sender,
            content=content,
            file=file
        )
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])
        return message
    
    def __str__(self):
        return f"Conversation {self.id} - {self.participants.count()} participants"


class PrivateMessage(models.Model):
    """Model to represent private messages within a conversation"""
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    content = models.TextField()
    file = models.FileField(
        upload_to=message_file_path, 
        blank=True, 
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
            )
        ]
    )
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MaxValueValidator(10 * 1024 * 1024)]  # 10MB max
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    is_encrypted = models.BooleanField(default=True)
    
    # Read receipt tracking
    read_by = models.ManyToManyField(
        User, 
        related_name='read_messages',
        blank=True
    )
    
    def __str__(self):
        return f"Message from {self.sender.get_full_name()} at {self.sent_at}"
    
    def mark_as_read(self, user):
        """Mark message as read by a specific user"""
        if user != self.sender and self.conversation.is_participant(user):
            self.read_by.add(user)
    
    def is_read_by(self, user):
        """Check if message has been read by a specific user"""
        return self.read_by.filter(id=user.id).exists()
    
    def save(self, *args, **kwargs):
        # Set file metadata if file is provided
        if self.file and not self.file_size:
            self.file_name = os.path.basename(self.file.name)
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class ForumCategory(models.Model):
    """Model to represent forum categories"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_categories'
    )
    allowed_user_types = models.JSONField(
        default=list,
        help_text='List of user types allowed to participate in this category'
    )
    
    def __str__(self):
        return self.name


class ForumThread(models.Model):
    """Model to represent a forum thread"""
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ForumCategory,
        on_delete=models.CASCADE,
        related_name='threads'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forum_threads'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Increment the views counter"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
        
    class Meta:
        ordering = ['-is_pinned', '-updated_at']


class ForumThreadFile(models.Model):
    """Model to handle files attached to forum threads"""
    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(
        upload_to=forum_file_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
            )
        ]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(
        validators=[MaxValueValidator(10 * 1024 * 1024)]  # 10MB max
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"File: {self.file_name} for {self.thread.title}"
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        if not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class ForumPost(models.Model):
    """Model to represent posts within a forum thread"""
    thread = models.ForeignKey(
        ForumThread,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='forum_posts'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_reported = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Post by {self.author.get_full_name()} in {self.thread.title}"


class ForumPostFile(models.Model):
    """Model to handle files attached to forum posts"""
    post = models.ForeignKey(
        ForumPost,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(
        upload_to=forum_file_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt']
            )
        ]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(
        validators=[MaxValueValidator(10 * 1024 * 1024)]  # 10MB max
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"File: {self.file_name} for post {self.post.id}"
    
    def save(self, *args, **kwargs):
        if not self.file_name:
            self.file_name = os.path.basename(self.file.name)
        if not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)


class UserTypingStatus(models.Model):
    """Model to track user typing status in conversations"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='typing_statuses'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='typing_users'
    )
    is_typing = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'conversation')
    
    def __str__(self):
        status = "typing" if self.is_typing else "not typing"
        return f"{self.user.get_full_name()} is {status} in conversation {self.conversation.id}"


class Notification(models.Model):
    """Model to store user notifications"""
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('forum_reply', 'Forum Reply'),
        ('assignment', 'Client Assignment'),
        ('system', 'System Notification'),
    )
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    related_conversation = models.ForeignKey(
        Conversation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    related_thread = models.ForeignKey(
        ForumThread,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    def __str__(self):
        return f"{self.notification_type} for {self.recipient.get_full_name()}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])


class MessageRateLimit(models.Model):
    """Model to track message rate limiting"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='rate_limit'
    )
    message_count = models.PositiveIntegerField(default=0)
    reset_at = models.DateTimeField()
    
    def __str__(self):
        return f"Rate limit for {self.user.get_full_name()}"
    
    def increment(self):
        """Increment message count and check if user has reached the limit"""
        # Reset counter if the reset time has passed
        if timezone.now() >= self.reset_at:
            self.message_count = 0
            self.reset_at = timezone.now() + timezone.timedelta(minutes=1)
        
        # Increment counter
        self.message_count += 1
        self.save()
        
        # Return True if under limit, False if over
        return self.message_count <= 10  # 10 messages per minute
    
    @classmethod
    def check_rate_limit(cls, user):
        """Check if user has exceeded rate limit"""
        rate_limit, created = cls.objects.get_or_create(
            user=user,
            defaults={'reset_at': timezone.now() + timezone.timedelta(minutes=1)}
        )
        return rate_limit.increment()



class MessageReaction(models.Model):
    """Model to represent reactions to messages"""
    REACTION_CHOICES = (
        ('like', 'Like'),
        ('love', 'Love'),
        ('laugh', 'Laugh'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    )
    
    message = models.ForeignKey(
        PrivateMessage,
        on_delete=models.CASCADE,
        related_name='reactions'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_reactions'
    )
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('message', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} reacted with {self.reaction_type} to message {self.message.id}"
    def save(self, *args, **kwargs):
        # Ensure the reaction type is valid
        if self.reaction_type not in dict(self.REACTION_CHOICES):
            raise ValueError("Invalid reaction type")
        super().save(*args, **kwargs)
    def get_reaction_count(self):
        """Get the count of reactions for this message"""
        return self.message.reactions.count()
    def get_reaction_summary(self):
        """Get a summary of reactions for this message"""
        summary = {}
        for reaction in self.message.reactions.all():
            summary[reaction.reaction_type] = summary.get(reaction.reaction_type, 0) + 1
        return summary
    def get_reaction_users(self):
        """Get a list of users who reacted to this message"""
        return [reaction.user for reaction in self.message.reactions.all()]
    def get_reaction_users_by_type(self, reaction_type):
        """Get a list of users who reacted with a specific type"""
        return [reaction.user for reaction in self.message.reactions.filter(reaction_type=reaction_type)]
    def get_reaction_summary_by_type(self):
        """Get a summary of reactions for this message by type"""
        summary = {}
        for reaction in self.message.reactions.all():
            summary[reaction.reaction_type] = summary.get(reaction.reaction_type, 0) + 1
        return summary
    def get_reaction_users_by_user(self, user):
        """Get a list of users who reacted with a specific type"""
        return [reaction.user for reaction in self.message.reactions.filter(user=user)]
   

