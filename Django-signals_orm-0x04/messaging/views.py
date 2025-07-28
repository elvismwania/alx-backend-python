# Django-signals_orm-0x04/messaging/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout

@login_required
def delete_user(request):
    """
    View to allow an authenticated user to delete their own account.
    Requires POST request for security.
    """
    if request.method == 'POST':
        user = request.user
        username = user.username # Store username before deletion for message
        user.delete() # This triggers the post_delete signal on the User model
        logout(request) # Log the user out after deletion
        messages.success(request, f"Your account '{username}' has been successfully deleted.")
        return redirect('home') # Redirect to a home page or login page
    # If not a POST request, render a confirmation page (optional, but good practice)
    return render(request, 'messaging/confirm_delete_account.html')

