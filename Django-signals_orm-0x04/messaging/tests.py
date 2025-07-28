from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessagingSignalTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')

    def test_notification_created_on_message(self):
        Message.objects.create(sender=self.user1, receiver=self.user2, content='Hello Bob')
        self.assertEqual(Notification.objects.count(), 1)
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.user2)
