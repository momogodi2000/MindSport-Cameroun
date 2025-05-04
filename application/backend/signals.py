
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import JournalEntry

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
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [professional.email],
                        fail_silently=True,
                    )
                except Exception:
                    # Log this error but don't break the save process
                    pass
    # Optionally, you can log the notification or handle it in another way
#     # Log the notification or handle it in another way
#     # For example, you could create a Notification model instance here
#     # or use Django's built-in logging framework to log the event 