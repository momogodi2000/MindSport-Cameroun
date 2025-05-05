
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




# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """Send real-time notification when a new notification is created"""
    if created:
        channel_layer = get_channel_layer()
        notification_group_name = f"notifications_{instance.recipient.id}"
        
        # Send to notification group
        async_to_sync(channel_layer.group_send)(
            notification_group_name,
            {
                "type": "new_notification",
                "notification_id": instance.id,
                "notification_type": instance.notification_type,
                "title": instance.title,
                "content": instance.content,
                "sender_id": instance.sender.id if instance.sender else None,
                "sender_name": instance.sender.get_full_name() if instance.sender else "System",
                "timestamp": instance.created_at.isoformat(),
                "is_read": instance.is_read,
                "conversation_id": instance.related_conversation.id if instance.related_conversation else None,
                "thread_id": instance.related_thread.id if instance.related_thread else None
            }
        )
