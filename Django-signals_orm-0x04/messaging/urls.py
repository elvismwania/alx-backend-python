# Django-signals_orm-0x04/messaging/urls.py

from django.urls import path
from . import views

app_name = 'messaging' # Namespace for this app's URLs

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_account'),
    # Add other messaging-related URLs here as needed
]
