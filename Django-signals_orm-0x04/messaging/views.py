# Django-signals_orm-0x04/messaging/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db import connection # For debugging query count
from django.views.decorators.cache import cache_page # For caching

from .models import Message, Notification, User # Import User model explicitly

@login_required
def delete_user(request):
    """
    View to allow an authenticated user to delete their own account.
    Requires POST request for security.
    """
    if request.method == 'POST':
        user = request.user
        username = user.username
        user.delete() # This triggers the post_delete signal on the User model
        logout(request) # Log the user out after deletion
        messages.success(request, f"Your account '{username}' has been successfully deleted.")
        return redirect('home') # Redirect to a home page or login page
    return render(request, 'messaging/confirm_delete_account.html')

@cache_page(60) # Cache this view for 60 seconds
@login_required
def inbox_and_conversation_view(request, message_id=None):
    """
    Displays the user's inbox (unread messages) and, optionally,
    a specific threaded conversation.
    """
    current_user = request.user
    context = {}

    # Task 4: Custom ORM Manager for Unread Messages
    # Use the custom manager to get unread messages for the current user,
    # optimized with .only()
    unread_messages = Message.unread_messages.for_user(current_user)
    context['unread_messages'] = unread_messages

    # Task 3: Leverage Advanced ORM Techniques for Threaded Conversations
    conversation_messages = []
    selected_message = None
    if message_id:
        try:
            # Fetch the root message of the conversation
            # Use select_related for sender/receiver to avoid N+1 for the root message
            selected_message = Message.objects.select_related('sender', 'receiver').get(pk=message_id)

            # Mark the selected message as read if it's for the current user and unread
            if selected_message.receiver == current_user and not selected_message.read:
                selected_message.read = True
                selected_message.save(update_fields=['read']) # Only update the 'read' field

            # Fetch the entire thread using the get_thread method
            # This method itself uses select_related for replies
            conversation_messages = selected_message.get_thread()

            context['selected_message'] = selected_message
            context['conversation_messages'] = conversation_messages

        except Message.DoesNotExist:
            messages.error(request, "The requested conversation message does not exist.")
            return redirect('messaging:inbox_and_conversation') # Redirect to inbox if message not found

    # Debugging query count (for demonstration of ORM optimization)
    # This will show the number of queries executed for this view
    print(f"Total queries for this view: {len(connection.queries)}")

    return render(request, 'messaging/inbox_and_conversation.html', context)

