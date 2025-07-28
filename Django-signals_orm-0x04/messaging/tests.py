from django.test import TestCase

# Create your tests here.

from django.contrib.auth.models import User
from .models import Message, Notification

class NotificationSignalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='sender', password='pass')
        self.user2 = User.objects.create_user(username='receiver', password='pass')

    def test_notification_created_on_message(self):
        msg = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hello")
        notification = Notification.objects.filter(user=self.user2, message=msg)
        self.assertTrue(notification.exists())
