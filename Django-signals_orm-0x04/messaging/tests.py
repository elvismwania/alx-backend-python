# Django-signals_orm-0x04/messaging/tests.py

from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Message, Notification, MessageHistory
from django.db.models import signals # Import signals module to disconnect
from messaging.signals import create_notification_on_message, log_message_edit, cleanup_user_data_on_delete # Import signal handlers

class MessageSignalTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username='sender_user', password='password123')
        cls.user2 = User.objects.create_user(username='receiver_user', password='password123')
        cls.user3 = User.objects.create_user(username='another_user', password='password123')


    def setUp(self):
        # Ensure signals are connected for tests that rely on them
        post_save.connect(create_notification_on_message, sender=Message)
        pre_save.connect(log_message_edit, sender=Message)
        post_delete.connect(cleanup_user_data_on_delete, sender=User) # Connect the new signal

    def tearDown(self):
        # Disconnect signals after each test to prevent interference between tests
        post_save.disconnect(create_notification_on_message, sender=Message)
        pre_save.disconnect(log_message_edit, sender=Message)
        post_delete.disconnect(cleanup_user_data_on_delete, sender=User) # Disconnect the new signal

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
        Test that MessageHistory is created, 'edited' flag is set, and 'edited_by' is correct
        when a message is updated.
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
        self.assertEqual(history_entry.edited_by, self.user1) # Check edited_by

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
        self.assertEqual(history_entry_2.edited_by, self.user1) # Check edited_by again
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

        # Retrieve from DB and save again without content change
        message_from_db = Message.objects.get(pk=message.pk)
        message_from_db.save()
        self.assertEqual(MessageHistory.objects.count(), 0)

    def test_user_data_cleanup_on_delete(self):
        """
        Test that messages, notifications, and message histories are deleted
        when a user account is deleted.
        """
        # Create messages, notifications, and history for user1 and user2
        # Message 1: user1 sends to user2
        msg1 = Message.objects.create(sender=self.user1, receiver=self.user2, content="Hi user2!")
        # Message 2: user2 sends to user1
        msg2 = Message.objects.create(sender=self.user2, receiver=self.user1, content="Hi user1!")
        # Message 3: user1 sends to user3 (unrelated user)
        msg3 = Message.objects.create(sender=self.user1, receiver=self.user3, content="Hi user3!")

        # Edit msg1 to create history for user1 as editor
        msg1.content = "Hi user2! (edited)"
        msg1.save() # This creates a MessageHistory entry for msg1, edited by user1

        # Edit msg2 to create history for user2 as editor
        msg2.content = "Hi user1! (edited)"
        msg2.save() # This creates a MessageHistory entry for msg2, edited by user2

        # Check initial counts
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Message.objects.count(), 3)
        self.assertEqual(Notification.objects.count(), 3) # 3 messages -> 3 notifications
        self.assertEqual(MessageHistory.objects.count(), 2) # 2 edits -> 2 history entries

        # Get the IDs of messages and history related to user1 before deletion
        msg1_id = msg1.id
        msg3_id = msg3.id # msg3 sent by user1
        history_for_msg1_id = MessageHistory.objects.filter(message=msg1).first().id
        history_edited_by_user1_count = MessageHistory.objects.filter(edited_by=self.user1).count()

        # Delete user1
        self.user1.delete()

        # Verify user1 is deleted
        self.assertEqual(User.objects.count(), 2)
        self.assertFalse(User.objects.filter(username='sender_user').exists())

        # Verify messages related to user1 are deleted (due to CASCADE)
        self.assertFalse(Message.objects.filter(id=msg1_id).exists()) # msg1 sent by user1
        self.assertFalse(Message.objects.filter(id=msg3_id).exists()) # msg3 sent by user1
        # msg2 should still exist as user2 is sender and user1 is receiver (CASCADE on receiver will delete it)
        # Re-think: If user1 is sender, msg1 is deleted. If user1 is receiver, msg2 is deleted.
        # So, all messages where user1 is involved (sender or receiver) should be deleted.
        self.assertEqual(Message.objects.count(), 0) # All 3 messages should be gone.

        # Verify notifications related to user1 or their messages are deleted (due to CASCADE)
        self.assertEqual(Notification.objects.count(), 0)

        # Verify message histories related to user1's messages or edited by user1 are deleted
        self.assertEqual(MessageHistory.objects.count(), 0) # Both history entries should be gone.
                                                           # History for msg1 (edited by user1) deleted by signal.
                                                           # History for msg2 (edited by user2) deleted by CASCADE on message.

        # Test the delete_user view (requires a client and login)
        client = Client()
        # Create a temporary user for view testing
        temp_user = User.objects.create_user(username='temp_deleter', password='testpassword')
        client.login(username='temp_deleter', password='testpassword')

        # Post to the delete_user view
        response = client.post('/messaging/delete-account/', follow=True) # Use follow=True for redirect

        # Check for successful deletion message
        self.assertContains(response, "Your account 'temp_deleter' has been successfully deleted.")
        # Check that the user is no longer authenticated
        self.assertFalse(response.context['user'].is_authenticated)
        # Check that the user count has decreased
        self.assertEqual(User.objects.count(), 1) # user2 and user3 remain, temp_user is gone.

