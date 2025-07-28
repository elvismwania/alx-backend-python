# Django-signals_orm-0x04/messaging/signals.py

from django.db.models.signals import post_save, pre_save, post_delete
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
    It also sets the 'edited_by' field in MessageHistory to the message's sender,
    assuming the sender is the one editing their own message.
    """
    if instance.pk: # Check if the instance already exists (i.e., it's an update, not a creation)
        try:
            # Retrieve the old instance from the database
            old_instance = Message.objects.get(pk=instance.pk)
            # If the content has changed, log it
            if old_instance.content != instance.content:
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content,
                    edited_by=instance.sender # Assuming the sender is the one editing the message
                )
                # Set the 'edited' flag on the message
                instance.edited = True
                print(f"Message ID {instance.pk} content changed. Old content logged to history by {instance.sender.username}.")
        except Message.DoesNotExist:
            # This should ideally not happen if instance.pk exists,
            # but it's good practice to handle the case where the object
            # might have been deleted between retrieval and pre_save.
            pass

@receiver(post_delete, sender=User)
def cleanup_user_data_on_delete(sender, instance, **kwargs):
    """
    Signal handler to clean up user-related data after a User account is deleted.
    Messages and Notifications are largely handled by CASCADE.
    This signal specifically ensures MessageHistory entries where the deleted user
    was the 'edited_by' person are also removed, as 'on_delete=SET_NULL' would
    otherwise leave them with a null 'edited_by' field.
    """
    user_id = instance.id
    username = instance.username
    print(f"User '{username}' (ID: {user_id}) is being deleted. Cleaning up related data...")

    # Messages sent by the user (will be CASCADE deleted if on_delete=CASCADE on sender)
    # Message.objects.filter(sender=instance).delete() # Redundant if CASCADE is set

    # Messages received by the user (will be CASCADE deleted if on_delete=CASCADE on receiver)
    # Message.objects.filter(receiver=instance).delete() # Redundant if CASCADE is set

    # Notifications for the user (will be CASCADE deleted if on_delete=CASCADE on user)
    # Notification.objects.filter(user=instance).delete() # Redundant if CASCADE is set

    # MessageHistory entries where this user was the editor
    # This is important because 'edited_by' has on_delete=models.SET_NULL,
    # so these wouldn't be automatically deleted.
    history_entries_edited_by_user = MessageHistory.objects.filter(edited_by=instance)
    count = history_entries_edited_by_user.count()
    if count > 0:
        history_entries_edited_by_user.delete()
        print(f"Deleted {count} MessageHistory entries where '{username}' was the editor.")
    else:
        print(f"No MessageHistory entries found where '{username}' was the editor.")

    print(f"Cleanup for user '{username}' (ID: {user_id}) completed.")


