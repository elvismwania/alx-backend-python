from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    user_id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)
    
    username = None
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS =["first_name", "last_name"]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class Conversation(models.Model):
  participants = models.ManyToManyField(User, related_name="conversations")
  created_at = models.DateTimeField(auto_now_add=True)
  conversation_id = models.CharField(max_length=100, unique=True)
  
  def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    message_body = models.TextField()
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sent_at = models.DateTimeField(auto_now_add=True)
    message_id = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ["sent_at"]

    def __str__(self):
        return f"Message {self.id} from {self.sender} in {self.conversation}"
    