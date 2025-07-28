# Django-signals_orm-0x04/messaging/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.db.models import signals # Import signals module to disconnect
from messaging.signals import create_notification_on_message, log_message_edit # Import signal handlers

class MessageSignalTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username='sender_user', password='password123')
        cls.user2 = User.objects.create_user(username='receiver_user', password='password123')

    def setUp(self):
        # Ensure signals are connected for tests that rely on them
        post_save.connect(create_notification_on_message, sender=Message)
        pre_save.connect(log_message_edit, sender=Message)

    def tearDown(self):
        # Disconnect signals after each test to prevent interference between tests
        post_save.disconnect(create_notification_on_message, sender=Message)
        pre_save.disconnect(log_message_edit, sender=Message)

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
        self.assertFalse(message.edited) # Should not be edited on creation


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

    def test_message_edit_history(self):
        """
        Test that MessageHistory is created and 'edited' flag is set when a message is updated.
        """
        # Create an initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message content."
        )
        self.assertFalse(message.edited)
        self.assertEqual(MessageHistory.objects.count(), 0)

        # Update the message content
        old_content = message.content
        message.content = "New, edited message content."
        message.save()

        # Check that a MessageHistory entry was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history_entry = MessageHistory.objects.first()

        self.assertEqual(history_entry.message, message)
        self.assertEqual(history_entry.old_content, old_content)

        # Retrieve the message again from DB to ensure 'edited' flag is saved
        updated_message = Message.objects.get(pk=message.pk)
        self.assertTrue(updated_message.edited)

        # Update again to ensure another history entry is created
        old_content_2 = updated_message.content
        updated_message.content = "Second edit."
        updated_message.save()

        self.assertEqual(MessageHistory.objects.count(), 2)
        history_entry_2 = MessageHistory.objects.order_by('-edited_at').first()
        self.assertEqual(history_entry_2.old_content, old_content_2)
        self.assertTrue(updated_message.edited)

    def test_no_history_on_message_creation(self):
        """
        Test that no MessageHistory is created when a new message is first created.
        """
        self.assertEqual(MessageHistory.objects.count(), 0)
        Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="A brand new message."
        )
        self.assertEqual(MessageHistory.objects.count(), 0) # Should still be 0

    def test_no_history_on_no_content_change(self):
        """
        Test that no MessageHistory is created if a message is saved but content doesn't change.
        """
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Content that won't change."
        )
        self.assertEqual(MessageHistory.objects.count(), 0)

        # Save without changing content
        message.save()
        self.assertEqual(MessageHistory.objects.count(), 0) # Still 0

        # Change a non-content field (e.g., timestamp, though auto_now_add makes this tricky)
        # For demonstration, let's assume we could change another field without content change
        # In a real scenario, you might have other fields.
        # For simplicity, we'll just re-save and expect no history if content is identical.
        message_from_db = Message.objects.get(pk=message.pk)
        message_from_db.save() # Saving without content change
        self.assertEqual(MessageHistory.objects.count(), 0)

