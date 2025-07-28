
# Django-signals_orm-0x04/messaging/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from .managers import UnreadMessagesManager # Import the custom manager

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False) # Field to track if message has been edited
    # Self-referential ForeignKey for threading: a reply points to its parent message
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies' # Allows accessing replies from a parent message: message.replies.all()
    )
    read = models.BooleanField(default=False) # New field to indicate if a message has been read

    # Default manager
    objects = models.Manager()
    # Custom manager for unread messages, renamed to 'unread'
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."

    def get_thread(self):
        """
        Recursively fetches all replies to this message.
        This method uses select_related for sender/receiver on replies for optimization.
        """
        # Optimized fetching of direct replies with sender/receiver preloaded
        replies = self.replies.all().select_related('sender', 'receiver').order_by('timestamp')
        threaded_replies = []
        for reply in replies:
            # Recursively get replies for each direct reply
            threaded_replies.append({
                'message': reply,
                'replies': reply.get_thread() # Recursive call
            })
        return threaded_replies


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='related_notifications', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"Notification for {self.user.username} about message from {self.message.sender.username}"

class MessageHistory(models.Model):
    """
    Model to store historical versions of messages when they are edited.
    """
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User, related_name='edited_messages_history', on_delete=models.SET_NULL, null=True)


    class Meta:
        ordering = ['-edited_at']
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"

    def __str__(self):
        editor_username = self.edited_by.username if self.edited_by else 'Unknown'
        return f"History for Message ID {self.message.id} by {editor_username} (Edited at {self.edited_at.strftime('%Y-%m-%d %H:%M')})"

