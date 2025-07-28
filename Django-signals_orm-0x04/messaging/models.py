# Django-signals_orm-0x04/messaging/models.py

from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False) # New field to track if message has been edited

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username}: {self.content[:50]}..."

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

    class Meta:
        ordering = ['-edited_at']
        verbose_name = "Message History"
        verbose_name_plural = "Message Histories"

    def __str__(self):
        return f"History for Message ID {self.message.id} (Edited at {self.edited_at.strftime('%Y-%m-%d %H:%M')})"


