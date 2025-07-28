

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _



# Custom User Model
class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('email address', unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True) #
    date_joined = models.DateTimeField(auto_now_add=True) 
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True) 
    is_online = models.BooleanField(default=False)
    
    # Explicitly define password field (overrides inherited one for clarity)
    password = models.CharField(_('password'), max_length=128)

    # Override username-related field requirements
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'  # You can change this to 'email' if you want email login

    def __str__(self):
        return self.username



# Conversation Model
class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField('User', related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.title or self.conversation_id}"



# Message Model
class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.sent_at}"
