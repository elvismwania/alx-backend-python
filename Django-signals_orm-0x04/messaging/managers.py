# Django-signals_orm-0x04/messaging/managers.py

from django.db import models

class UnreadMessagesManager(models.Manager):
    """
    Custom manager to filter unread messages for a specific user.
    """
    def unread_for_user(self, user):
        # Filters messages received by the user that are not yet read.
        # Uses .only() to retrieve only necessary fields for efficiency.
        return self.filter(receiver=user, read=False).only(
            'sender', 'receiver', 'content', 'timestamp', 'edited', 'parent_message', 'read'
        ).order_by('-timestamp')

