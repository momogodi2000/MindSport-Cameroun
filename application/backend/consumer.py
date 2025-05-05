import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.utils import timezone
import base64
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
import os

from .models import (
    Conversation, PrivateMessage, ForumThread, ForumPost,
    UserTypingStatus, Notification, MessageRateLimit, ClientAssignment,
    User, ForumCategory, ForumThreadFile, ForumPostFile
)

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.conversation_group_name = f"chat_{self.conversation_id}"
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has completed profile
        if not await self.check_profile_complete():
            await self.close()
            return
        
        # Check if user is part of the conversation
        if not await self.is_conversation_participant():
            await self.close()
            return
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send conversation history
        await self.send_conversation_history()

    async def disconnect(self, close_code):
        # Leave conversation group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )
        
        # Update typing status to false when disconnecting
        await self.update_typing_status(False)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        
        if message_type == "chat_message":
            # Process a new message
            content = text_data_json.get("message", "")
            file_data = text_data_json.get("file", None)
            
            # Check rate limiting
            if not await self.check_rate_limit():
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Rate limit exceeded. Please wait before sending more messages."
                }))
                return
            
            # Save and broadcast the message
            message = await self.save_message(content, file_data)
            
            # Encrypt message before sending
            encrypted_content = await self.encrypt_message(content)
            
            # Broadcast message to conversation group
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    "type": "chat_message",
                    "message_id": message.id,
                    "message": encrypted_content,
                    "sender_id": self.user.id,
                    "sender_name": self.user.get_full_name(),
                    "timestamp": message.sent_at.isoformat(),
                    "has_file": bool(message.file),
                    "file_url": message.file.url if message.file else None,
                    "file_name": message.file_name if message.file else None,
                }
            )
            
            # Create notifications for other participants
            await self.create_message_notifications(message)
            
        elif message_type == "typing_status":
            # Update and broadcast typing status
            is_typing = text_data_json.get("is_typing", False)
            await self.update_typing_status(is_typing)
            
            # Broadcast typing status to conversation group
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    "type": "typing_status",
                    "user_id": self.user.id,
                    "user_name": self.user.get_full_name(),
                    "is_typing": is_typing
                }
            )
            
        elif message_type == "read_receipt":
            # Process read receipt
            message_id = text_data_json.get("message_id")
            await self.mark_message_as_read(message_id)
            
            # Broadcast read receipt to conversation group
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    "type": "read_receipt",
                    "message_id": message_id,
                    "user_id": self.user.id,
                    "user_name": self.user.get_full_name(),
                    "timestamp": timezone.now().isoformat()
                }
            )

    # Handler for chat messages
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # Handler for typing status
    async def typing_status(self, event):
        await self.send(text_data=json.dumps(event))

    # Handler for read receipts
    async def read_receipt(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_profile_complete(self):
        """Check if user has completed their profile"""
        return self.user.is_profile_complete()

    @database_sync_to_async
    def is_conversation_participant(self):
        """Check if user is a participant in the conversation"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.is_participant(self.user)
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, file_data=None):
        """Save a new message to the database"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        
        # Handle file if provided
        file = None
        if file_data:
            # Decode base64 file data
            format, filestr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file_content = ContentFile(base64.b64decode(filestr), name=f'message_file.{ext}')
            
            # Create the message with file
            message = conversation.add_message(
                sender=self.user,
                content=content,
                file=file_content
            )
        else:
            # Create message without file
            message = conversation.add_message(
                sender=self.user,
                content=content
            )
            
        return message

    @database_sync_to_async
    def update_typing_status(self, is_typing):
        """Update user typing status"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        typing_status, created = UserTypingStatus.objects.get_or_create(
            user=self.user,
            conversation=conversation,
            defaults={'is_typing': is_typing}
        )
        
        if not created:
            typing_status.is_typing = is_typing
            typing_status.save()

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark a message as read by the current user"""
        try:
            message = PrivateMessage.objects.get(id=message_id)
            message.mark_as_read(self.user)
            return True
        except PrivateMessage.DoesNotExist:
            return False

    @database_sync_to_async
    def check_rate_limit(self):
        """Check if user has exceeded rate limit"""
        return MessageRateLimit.check_rate_limit(self.user)

    @database_sync_to_async
    def encrypt_message(self, content):
        """Encrypt message content"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            encryption_key = conversation.encryption_key
            
            # Create a Fernet cipher with the encryption key
            fernet = Fernet(base64.urlsafe_b64encode(encryption_key.encode()[:32].ljust(32, b'\0')))
            
            # Encrypt the content
            encrypted_content = fernet.encrypt(content.encode()).decode()
            return encrypted_content
        except Exception as e:
            # If encryption fails, return original content
            return content

    @database_sync_to_async
    def create_message_notifications(self, message):
        """Create notifications for conversation participants"""
        conversation = Conversation.objects.get(id=self.conversation_id)
        recipients = conversation.participants.exclude(id=self.user.id)
        
        for recipient in recipients:
            Notification.objects.create(
                recipient=recipient,
                sender=self.user,
                notification_type='message',
                title=f'New message from {self.user.get_full_name()}',
                content=message.content[:50] + '...' if len(message.content) > 50 else message.content,
                related_conversation=conversation
            )

    @database_sync_to_async
    def send_conversation_history(self):
        """Send conversation history to the user"""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            messages = conversation.messages.order_by('sent_at')[:100]  # Limit to last 100 messages
            
            # Get encryption key
            encryption_key = conversation.encryption_key
            fernet = Fernet(base64.urlsafe_b64encode(encryption_key.encode()[:32].ljust(32, b'\0')))
            
            history = []
            for msg in messages:
                # Try to encrypt content for consistency
                try:
                    encrypted_content = fernet.encrypt(msg.content.encode()).decode()
                except:
                    encrypted_content = msg.content
                    
                history.append({
                    "message_id": msg.id,
                    "message": encrypted_content,
                    "sender_id": msg.sender.id,
                    "sender_name": msg.sender.get_full_name(),
                    "timestamp": msg.sent_at.isoformat(),
                    "has_file": bool(msg.file),
                    "file_url": msg.file.url if msg.file else None,
                    "file_name": msg.file_name if msg.file else None,
                    "read_by": [user.id for user in msg.read_by.all()]
                })
            
            # Mark all messages as read by this user
            for msg in messages:
                if msg.sender != self.user:
                    msg.mark_as_read(self.user)
            
            # Send history to the user
            await self.send(text_data=json.dumps({
                "type": "conversation_history",
                "history": history
            }))
            
        except Conversation.DoesNotExist:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Conversation not found"
            }))


class ForumConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.thread_id = self.scope["url_route"]["kwargs"].get("thread_id")
        self.category_id = self.scope["url_route"]["kwargs"].get("category_id")
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user has completed profile
        if not await self.check_profile_complete():
            await self.close()
            return
            
        # If thread_id is provided, join that thread's group
        if self.thread_id:
            self.group_name = f"forum_thread_{self.thread_id}"
            
            # Check if thread exists and user has access
            if not await self.can_access_thread():
                await self.close()
                return
                
        # If category_id is provided, join that category's group
        elif self.category_id:
            self.group_name = f"forum_category_{self.category_id}"
            
            # Check if category exists and user has access
            if not await self.can_access_category():
                await self.close()
                return
                
        # If neither is provided, join the general forum group
        else:
            self.group_name = "forum_general"
        
        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # If on a thread, increment view count
        if self.thread_id:
            await self.increment_thread_views()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        
        if message_type == "new_thread":
            # Create new thread
            title = text_data_json.get("title")
            content = text_data_json.get("content")
            category_id = text_data_json.get("category_id")
            file_data = text_data_json.get("file", None)
            
            # Check if user can create threads
            if not await self.can_create_thread():
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "You don't have permission to create threads in this category."
                }))
                return
            
            # Check rate limiting
            if not await self.check_rate_limit():
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Rate limit exceeded. Please wait before creating more content."
                }))
                return
                
            # Create thread
            thread = await self.create_thread(title, content, category_id, file_data)
            
            # Broadcast to category group
            category_group = f"forum_category_{category_id}"
            await self.channel_layer.group_send(
                category_group,
                {
                    "type": "new_thread_notification",
                    "thread_id": thread.id,
                    "title": thread.title,
                    "author_id": self.user.id,
                    "author_name": self.user.get_full_name(),
                    "category_id": category_id,
                    "timestamp": thread.created_at.isoformat()
                }
            )
            
            # Broadcast to general forum group
            await self.channel_layer.group_send(
                "forum_general",
                {
                    "type": "new_thread_notification",
                    "thread_id": thread.id,
                    "title": thread.title,
                    "author_id": self.user.id,
                    "author_name": self.user.get_full_name(),
                    "category_id": category_id,
                    "timestamp": thread.created_at.isoformat()
                }
            )
            
        elif message_type == "new_post":
            # Create new post in thread
            thread_id = text_data_json.get("thread_id")
            content = text_data_json.get("content")
            file_data = text_data_json.get("file", None)
            
            # Check if user can reply to thread
            if not await self.can_reply_to_thread(thread_id):
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "You don't have permission to reply to this thread or the thread is locked."
                }))
                return
                
            # Check rate limiting
            if not await self.check_rate_limit():
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": "Rate limit exceeded. Please wait before posting more content."
                }))
                return
                
            # Create post
            post = await self.create_post(thread_id, content, file_data)
            
            # Get thread info
            thread_info = await self.get_thread_info(thread_id)
            
            # Broadcast to thread group
            thread_group = f"forum_thread_{thread_id}"
            await self.channel_layer.group_send(
                thread_group,
                {
                    "type": "new_post_notification",
                    "post_id": post.id,
                    "content": post.content,
                    "author_id": self.user.id,
                    "author_name": self.user.get_full_name(),
                    "thread_id": thread_id,
                    "thread_title": thread_info["title"],
                    "timestamp": post.created_at.isoformat(),
                    "has_file": bool(post.files.exists()),
                    "files": [
                        {
                            "url": file.file.url,
                            "name": file.file_name,
                            "size": file.file_size
                        } for file in post.files.all()
                    ]
                }
            )
            
            # Create notifications for thread author and participants
            await self.create_forum_notifications(post, thread_info)

    # Handler for new thread notifications
    async def new_thread_notification(self, event):
        await self.send(text_data=json.dumps(event))

    # Handler for new post notifications
    async def new_post_notification(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def check_profile_complete(self):
        """Check if user has completed their profile"""
        return self.user.is_profile_complete()

    @database_sync_to_async
    def can_access_thread(self):
        """Check if thread exists and user has access"""
        try:
            thread = ForumThread.objects.select_related('category').get(id=self.thread_id)
            category = thread.category
            
            # Check if user type is allowed in this category
            user_type = self.user.user_type
            allowed_user_types = category.allowed_user_types
            
            return user_type in allowed_user_types
        except ForumThread.DoesNotExist:
            return False

    @database_sync_to_async
    def can_access_category(self):
        """Check if category exists and user has access"""
        try:
            category = ForumCategory.objects.get(id=self.category_id)
            
            # Check if user type is allowed in this category
            user_type = self.user.user_type
            allowed_user_types = category.allowed_user_types
            
            return user_type in allowed_user_types
        except ForumCategory.DoesNotExist:
            return False

    @database_sync_to_async
    def can_create_thread(self):
        """Check if user can create threads in the category"""
        try:
            category = ForumCategory.objects.get(id=self.category_id)
            
            # Check if user type is allowed in this category
            user_type = self.user.user_type
            allowed_user_types = category.allowed_user_types
            
            return user_type in allowed_user_types
        except ForumCategory.DoesNotExist:
            return False

    @database_sync_to_async
    def can_reply_to_thread(self, thread_id):
        """Check if user can reply to the thread"""
        try:
            thread = ForumThread.objects.select_related('category').get(id=thread_id)
            
            # Check if thread is locked
            if thread.is_locked:
                return False
                
            # Check if user type is allowed in this category
            category = thread.category
            user_type = self.user.user_type
            allowed_user_types = category.allowed_user_types
            
            return user_type in allowed_user_types
        except ForumThread.DoesNotExist:
            return False

    @database_sync_to_async
    def check_rate_limit(self):
        """Check if user has exceeded rate limit"""
        return MessageRateLimit.check_rate_limit(self.user)

    @database_sync_to_async
    def create_thread(self, title, content, category_id, file_data=None):
        """Create a new forum thread"""
        category = ForumCategory.objects.get(id=category_id)
        
        # Create thread
        thread = ForumThread.objects.create(
            title=title,
            category=category,
            author=self.user,
            content=content
        )
        
        # Handle file if provided
        if file_data:
            from .models import ForumThreadFile
            
            # Decode base64 file data
            format, filestr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file_content = ContentFile(base64.b64decode(filestr), name=f'thread_file.{ext}')
            
            # Create file
            ForumThreadFile.objects.create(
                thread=thread,
                file=file_content
            )
            
        return thread

    @database_sync_to_async
    def create_post(self, thread_id, content, file_data=None):
        """Create a new forum post"""
        thread = ForumThread.objects.get(id=thread_id)
        
        # Update thread's updated_at timestamp
        thread.updated_at = timezone.now()
        thread.save(update_fields=['updated_at'])
        
        # Create post
        post = ForumPost.objects.create(
            thread=thread,
            author=self.user,
            content=content
        )
        
        # Handle file if provided
        if file_data:
            from .models import ForumPostFile
            
            # Decode base64 file data
            format, filestr = file_data.split(';base64,')
            ext = format.split('/')[-1]
            file_content = ContentFile(base64.b64decode(filestr), name=f'post_file.{ext}')
            
            # Create file
            ForumPostFile.objects.create(
                post=post,
                file=file_content
            )
            
        return post

    @database_sync_to_async
    def get_thread_info(self, thread_id):
        """Get basic info about a thread"""
        thread = ForumThread.objects.select_related('author', 'category').get(id=thread_id)
        return {
            "id": thread.id,
            "title": thread.title,
            "author_id": thread.author.id,
            "category_id": thread.category.id
        }

    @database_sync_to_async
    def increment_thread_views(self):
        """Increment thread view count"""
        try:
            thread = ForumThread.objects.get(id=self.thread_id)
            thread.increment_views()
        except ForumThread.DoesNotExist:
            pass

    @database_sync_to_async
    def create_forum_notifications(self, post, thread_info):
        """Create notifications for forum activity"""
        # Get thread
        thread = ForumThread.objects.get(id=thread_info["id"])
        
        # Notify thread author if not the current user
        if thread.author.id != self.user.id:
            Notification.objects.create(
                recipient=thread.author,
                sender=self.user,
                notification_type='forum_reply',
                title=f'New reply in your thread "{thread.title}"',
                content=post.content[:50] + '...' if len(post.content) > 50 else post.content,
                related_thread=thread
            )
        
        # Get unique authors in this thread (excluding current user and thread author)
        unique_authors = ForumPost.objects.filter(
            thread=thread
        ).exclude(
            author__in=[self.user, thread.author]
        ).values_list('author', flat=True).distinct()
        
        # Notify other participants
        for author_id in unique_authors:
            try:
                recipient = User.objects.get(id=author_id)
                Notification.objects.create(
                    recipient=recipient,
                    sender=self.user,
                    notification_type='forum_reply',
                    title=f'New activity in thread "{thread.title}"',
                    content=post.content[:50] + '...' if len(post.content) > 50 else post.content,
                    related_thread=thread
                )
            except User.DoesNotExist:
                continue


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # User-specific notification group
        self.notification_group_name = f"notifications_{self.user.id}"
        
        # Join notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications count
        await self.send_unread_count()

    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        
        if message_type == "mark_as_read":
            # Mark notification as read
            notification_id = text_data_json.get("notification_id")
            await self.mark_notification_read(notification_id)
            
            # Send updated unread count
            await self.send_unread_count()
            
        elif message_type == "mark_all_as_read":
            # Mark all notifications as read
            await self.mark_all_notifications_read()
            
            # Send updated unread count
            await self.send_unread_count()
            
        elif message_type == "get_notifications":
            # Send list of notifications
            page = text_data_json.get("page", 1)
            await self.send_notifications(page)

    # Handler for new notification
    async def new_notification(self, event):
        await self.send(text_data=json.dumps(event))
        
        # Also send updated unread count
        await self.send_unread_count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(id=notification_id, recipient=self.user)
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read"""
        Notification.objects.filter(recipient=self.user, is_read=False).update(is_read=True)

    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread notifications"""
        return Notification.objects.filter(recipient=self.user, is_read=False).count()

    async def send_unread_count(self):
        """Send unread notification count to user"""
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": count
        }))

    @database_sync_to_async
    def get_notifications(self, page=1):
        """Get paginated notifications for the user"""
        from django.core.paginator import Paginator
        
        notifications = Notification.objects.filter(
            recipient=self.user
        ).order_by('-created_at')
        
        paginator = Paginator(notifications, 10)  # 10 notifications per page
        page_obj = paginator.get_page(page)
        
        notifications_data = []
        for notification in page_obj:
            notifications_data.append({
                "id": notification.id,
                "type": notification.notification_type,
                "title": notification.title,
                "content": notification.content,
                "sender_id": notification.sender.id if notification.sender else None,
                "sender_name": notification.sender.get_full_name() if notification.sender else "System",
                "timestamp": notification.created_at.isoformat(),
                "is_read": notification.is_read,
                "conversation_id": notification.related_conversation.id if notification.related_conversation else None,
                "thread_id": notification.related_thread.id if notification.related_thread else None
            })
            
        return {
            "notifications": notifications_data,
            "has_next": page_obj.has_next(),
            "has_prev": page_obj.has_previous(),
            "total_pages": paginator.num_pages
        }

    async def send_notifications(self, page=1):
        """Send paginated notifications to user"""
        data = await self.get_notifications(page)
        await self.send(text_data=json.dumps({
            "type": "notifications_list",
            **data
        }))