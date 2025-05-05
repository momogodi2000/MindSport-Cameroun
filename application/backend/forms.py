from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import (
    AnonymousQuestion, ContactMessage, MentorshipRelationship, 
    NewsletterSubscriber, SuccessStory, Thread, Comment,
    AppointmentRequest, AppointmentReview, AppointmentNote,
    JournalEntry, WellnessResource, ResourceCategory, 
    JournalTemplate, JournalPrompt, SupportGroupParticipant
)

# Get the custom User model
User = get_user_model()


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        
class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    sport = forms.ChoiceField(choices=User.SPORT_CHOICES, required=False)
    level = forms.ChoiceField(choices=User.LEVEL_CHOICES, required=False)
    qualifications = forms.CharField(max_length=255, required=False)
    years_experience = forms.IntegerField(
        min_value=0, 
        max_value=50, 
        required=False,
        widget=forms.NumberInput(attrs={'type': 'number'})
    )
    terms_accepted = forms.BooleanField(required=True)
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'user_type',
            'sport', 'level', 'qualifications', 'years_experience',
            'password1', 'password2', 'terms_accepted'
        ]
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'athlete':
            if not cleaned_data.get('sport'):
                self.add_error('sport', 'This field is required for athletes')
            if not cleaned_data.get('level'):
                self.add_error('level', 'This field is required for athletes')
        
        if user_type in ['psychologist', 'coach', 'nutritionist']:
            if not cleaned_data.get('qualifications'):
                self.add_error('qualifications', 'This field is required for professionals')
            if not cleaned_data.get('years_experience'):
                self.add_error('years_experience', 'This field is required for professionals')
        
        return cleaned_data
    
class AthleteProfileForm(forms.ModelForm):
    mobile_number = forms.CharField(max_length=20, required=True, 
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your mobile number'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_image', 'sport', 'level', 'town', 'quartier']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'sport': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'town': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your town'}),
            'quartier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your quartier'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-input'})
        }

    def __init__(self, *args, **kwargs):
        super(AthleteProfileForm, self).__init__(*args, **kwargs)
        # Set all fields as required
        for field in self.fields:
            self.fields[field].required = True

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if not image:
            raise forms.ValidationError("Profile image is required.")
        return image

class SocialSignupForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_type', 'sport', 'level', 'qualifications', 'years_experience']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-input'}),
            'sport': forms.Select(attrs={'class': 'form-input'}),
            'level': forms.Select(attrs={'class': 'form-input'}),
            'qualifications': forms.TextInput(attrs={'class': 'form-input'}),
            'years_experience': forms.NumberInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['terms_accepted'] = forms.BooleanField(
            required=True,
            widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded'}),
            label='I agree to the Terms of Service and Privacy Policy'
        )
        
        # Make fields required based on user type
        self.fields['sport'].required = False
        self.fields['level'].required = False
        self.fields['qualifications'].required = False
        self.fields['years_experience'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'athlete':
            if not cleaned_data.get('sport'):
                self.add_error('sport', 'This field is required for athletes')
            if not cleaned_data.get('level'):
                self.add_error('level', 'This field is required for athletes')
        
        if user_type in ['psychologist', 'coach', 'nutritionist']:
            if not cleaned_data.get('qualifications'):
                self.add_error('qualifications', 'This field is required for professionals')
            if not cleaned_data.get('years_experience'):
                self.add_error('years_experience', 'This field is required for professionals')
        
        return cleaned_data

class AppointmentRequestForm(forms.ModelForm):
    """Form for creating appointment requests"""
    class Meta:
        model = AppointmentRequest
        fields = ['specialist', 'date', 'time', 'duration', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit specialist choices to verified professionals
        self.fields['specialist'].queryset = User.objects.filter(
            is_verified_professional=True,
            account_status='active',
            user_type__in=['psychologist', 'coach', 'nutritionist']
        )

class AppointmentResponseForm(forms.ModelForm):
    """Form for specialists to respond to appointment requests"""
    class Meta:
        model = AppointmentRequest
        fields = ['response_message']
        widgets = {
            'response_message': forms.Textarea(attrs={'rows': 3}),
        }

class AppointmentReviewForm(forms.ModelForm):
    """Form for athletes to review completed appointments"""
    class Meta:
        model = AppointmentReview
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class AppointmentNoteForm(forms.ModelForm):
    """Form for adding notes to appointments"""
    class Meta:
        model = AppointmentNote
        fields = ['content', 'is_private']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }

class JournalEntryForm(forms.ModelForm):
    """Form for creating/editing journal entries"""
    class Meta:
        model = JournalEntry
        fields = ['title', 'content', 'mood', 'energy_level', 'stress_level', 'sleep_hours', 'tags', 'is_private', 'shared_with']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g., stress, training, recovery (comma-separated)'}),
            'sleep_hours': forms.NumberInput(attrs={'step': '0.5', 'min': '0', 'max': '24'}),
            'shared_with': forms.SelectMultiple(attrs={'class': 'select2-multiple'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter shared_with to only include coaches and psychologists
            self.fields['shared_with'].queryset = user.get_available_professionals()


class ResourceFilterForm(forms.Form):
    """Form for filtering wellness resources"""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search resources...'}))
    category = forms.ModelChoiceField(
        queryset=ResourceCategory.objects.all(),
        required=False,
        empty_label="All Categories"
    )
    content_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(WellnessResource.CONTENT_TYPE_CHOICES),
        required=False
    )
    tag = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Filter by tag...'}))


class JournalSearchForm(forms.Form):
    """Form for searching journal entries"""
    query = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search entries...'}))
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="From Date"
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="To Date"
    )
    mood = forms.ChoiceField(
        choices=[('', 'All Moods')] + list(JournalEntry.MOOD_CHOICES),
        required=False
    )
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Filter by tags (comma-separated)...'})
    )


class JournalTemplateForm(forms.ModelForm):
    """Form for creating/editing journal templates"""
    class Meta:
        model = JournalTemplate
        fields = ['title', 'description', 'structure', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'structure': forms.Textarea(attrs={'rows': 10, 'class': 'json-editor'}),
        }


class JournalPromptForm(forms.ModelForm):
    """Form for creating/editing journal prompts"""
    class Meta:
        model = JournalPrompt
        fields = ['text', 'category', 'is_active']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }


# Let's add functionality to register these in the admin panel
# admin.py
from django.contrib import admin
from .models import (
    ResourceCategory, WellnessResource, SavedResource, 
    ResourceRating, JournalEntry, JournalPrompt, JournalTemplate
)

@admin.register(ResourceCategory)
class ResourceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

@admin.register(WellnessResource)
class WellnessResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'content_type', 'created_by', 'created_at', 'published', 'featured']
    list_filter = ['category', 'content_type', 'published', 'featured', 'created_at']
    search_fields = ['title', 'description', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(SavedResource)
class SavedResourceAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'saved_at']
    list_filter = ['saved_at']
    search_fields = ['user__username', 'resource__title', 'notes']

@admin.register(ResourceRating)
class ResourceRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'resource__title', 'feedback']

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'title', 'mood', 'is_private']
    list_filter = ['mood', 'is_private', 'date', 'energy_level', 'stress_level']
    search_fields = ['user__username', 'title', 'content', 'tags']
    date_hierarchy = 'date'

@admin.register(JournalPrompt)
class JournalPromptAdmin(admin.ModelAdmin):
    list_display = ['text_preview', 'category', 'created_by', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['text', 'category']
    
    def text_preview(self, obj):
        return obj.text[:50] + ('...' if len(obj.text) > 50 else '')
    text_preview.short_description = 'Prompt Text'



@admin.register(JournalTemplate)
class JournalTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'is_public']
    list_filter = ['is_public']
    search_fields = ['title', 'description']



    from django import forms
    from django.core.exceptions import ValidationError
    from .models import (
        Thread, Comment, AnonymousQuestion, SuccessStory,
        MentorshipRelationship, SupportGroupParticipant
    )
    
class ThreadForm(forms.ModelForm):
        """Form for creating threads"""
        class Meta:
            model = Thread
            fields = ['title', 'category', 'content']
            widgets = {
                'content': forms.Textarea(attrs={'rows': 8}),
            }
        
        def clean_title(self):
            title = self.cleaned_data.get('title')
            if len(title) < 5:
                raise forms.ValidationError("Title must be at least 5 characters long.")
            return title
        
        def clean_content(self):
            content = self.cleaned_data.get('content')
            if len(content) < 20:
                raise forms.ValidationError("Content must be at least 20 characters long.")
            return content
    
class CommentForm(forms.ModelForm):
        """Form for creating comments"""
        class Meta:
            model = Comment
            fields = ['content']
            widgets = {
                'content': forms.Textarea(attrs={'rows': 5}),
            }
        
        def clean_content(self):
            content = self.cleaned_data.get('content')
            if len(content) < 5:
                raise forms.ValidationError("Comment must be at least 5 characters long.")
            return content
    
class AnonymousQuestionForm(forms.ModelForm):
        """Form for submitting anonymous questions"""
        class Meta:
            model = AnonymousQuestion
            fields = ['title', 'content']
            widgets = {
                'title': forms.TextInput(attrs={'placeholder': 'Your question title'}),
                'content': forms.Textarea(attrs={
                    'rows': 6, 
                    'placeholder': 'Describe your question in detail. This will be kept anonymous.'
                }),
            }
        
        def clean_title(self):
            title = self.cleaned_data.get('title')
            if len(title) < 10:
                raise forms.ValidationError("Title must be at least 10 characters long.")
            return title
        
        def clean_content(self):
            content = self.cleaned_data.get('content')
            if len(content) < 30:
                raise forms.ValidationError("Content must be at least 30 characters long.")
            return content
    
class SuccessStoryForm(forms.ModelForm):
        """Form for submitting success stories"""
        class Meta:
            model = SuccessStory
            fields = ['title', 'content', 'featured_image']
            widgets = {
                'title': forms.TextInput(attrs={'placeholder': 'Title of your success story'}),
                'content': forms.Textarea(attrs={
                    'rows': 10, 
                    'placeholder': 'Share your journey and how you overcame your challenges...'
                }),
            }
        
        def clean_title(self):
            title = self.cleaned_data.get('title')
            if len(title) < 10:
                raise forms.ValidationError("Title must be at least 10 characters long.")
            return title
        
        def clean_content(self):
            content = self.cleaned_data.get('content')
            if len(content) < 200:
                raise forms.ValidationError("Content must be at least 200 characters long to provide meaningful insight.")
            return content
    
class MentorshipApplicationForm(forms.ModelForm):
        """Form for applying to mentorship programs"""
        ROLE_CHOICES = (
            ('mentor', 'I want to be a mentor'),
            ('mentee', 'I want to be mentored'),
        )
        
        role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
        
        class Meta:
            model = MentorshipRelationship
            fields = ['goals']
            widgets = {
                'goals': forms.Textarea(attrs={
                    'rows': 6, 
                    'placeholder': 'What do you hope to achieve through this mentorship?'
                }),
            }
        
        def clean_goals(self):
            goals = self.cleaned_data.get('goals')
            if len(goals) < 50:
                raise forms.ValidationError("Please provide more details about your goals (at least 50 characters).")
            return goals
    
class SupportGroupRegistrationForm(forms.Form):
        """Form for registering to support groups"""
        reason = forms.CharField(
            widget=forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Why do you want to join this support group?'
            }),
            required=True
        )
        
        agreement = forms.BooleanField(
            label="I agree to respect the confidentiality of other group members and follow the group guidelines.",
            required=True
        )
        
        def clean_reason(self):
            reason = self.cleaned_data.get('reason')
            if len(reason) < 20:
                raise forms.ValidationError("Please provide a more detailed reason for joining (at least 20 characters).")
            return reason
    


