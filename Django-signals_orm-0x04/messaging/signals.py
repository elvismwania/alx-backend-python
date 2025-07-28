# Django-signals_orm-0x04/messaging/signals.py

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory
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

@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    """
    Signal handler to log the old content of a Message before it's updated.
    This runs *before* the save operation.
    """
    if instance.pk: # Check if the instance already exists (i.e., it's an update, not a creation)
        try:
            # Retrieve the old instance from the database
            old_instance = Message.objects.get(pk=instance.pk)
            # If the content has changed, log it
            if old_instance.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content
                )
                # Set the 'edited' flag on the message
                instance.edited = True
                print(f"Message ID {instance.pk} content changed. Old content logged to history.")
        except Message.DoesNotExist:
            # This should ideally not happen if instance.pk exists,
            # but it's good practice to handle the case where the object
            # might have been deleted between retrieval and pre_save.
            pass

