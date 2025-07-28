# Django-signals_orm-0x04/messaging/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification
from django.contrib.auth.models import User

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """
    Signal handler to create a Notification when a new Message is saved.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )
        print(f"Notification created for {instance.receiver.username} due to new message from {instance.sender.username}")
