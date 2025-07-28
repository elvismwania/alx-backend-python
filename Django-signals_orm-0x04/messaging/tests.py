# Django-signals_orm-0x04/messaging/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification
from django.db.models import signals # Import signals module to disconnect
from messaging.signals import create_notification_on_message # Import the signal handler

class MessageSignalTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username='sender_user', password='password123')
        cls.user2 = User.objects.create_user(username='receiver_user', password='password123')

    def setUp(self):
        # Disconnect the signal during tests to prevent interference,
        # then explicitly call the signal handler for testing purposes
        # or, in this case, test the signal's effect directly.
        # For post_save signals, it's often better to let it run and check the outcome.
        pass

    def test_notification_created_on_new_message(self):
        """
        Test that a Notification is automatically created when a new Message is saved.
        """
        # Ensure no notifications exist initially for receiver_user
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 0)

        # Create a new message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Hello there!"
        )

        # After message creation, a notification should exist
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)

        # Get the created notification
        notification = Notification.objects.get(user=self.user2)

        # Check if the notification is linked to the correct message and user
        self.assertEqual(notification.message, message)
        self.assertEqual(notification.user, self.user2)
        self.assertFalse(notification.is_read) # Should be unread by default

    def test_no_notification_on_message_update(self):
        """
        Test that no new Notification is created when an existing Message is updated.
        """
        # Create an initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Initial content"
        )
        # Ensure one notification exists from the initial creation
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)

        # Update the message (this should not trigger a new notification)
        message.content = "Updated content"
        message.save()

        # The count of notifications should remain 1
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 1)
