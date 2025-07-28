from django.db import models
from django.contrib.auth.models import User

class UnreadMessagesManager(models.Manager):
    def for_user(self, user):
        return self.get_queryset().filter(receiver=user, read=False).only(
            'id', 'sender', 'content', 'timestamp'
        )

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='edited_messages'
    )
    parent_message = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )
    read = models.BooleanField(default=False)  # ✅ New field to track if the message was read

    objects = models.Manager()              # default manager
    unread = UnreadMessagesManager()        # ✅ custom manager for unread messages

    def __str__(self):
        return f'Message #{self.id} from {self.sender} to {self.receiver}'
