# Django-signals_orm-0x04/messaging/urls.py

from django.urls import path
from . import views

app_name = 'messaging' # Namespace for this app's URLs

urlpatterns = [
    path('delete-account/', views.delete_user, name='delete_account'),
    # URL for displaying the inbox and optionally a specific conversation
    path('inbox/', views.inbox_and_conversation_view, name='inbox_and_conversation'),
    path('inbox/<int:message_id>/', views.inbox_and_conversation_view, name='inbox_and_conversation_detail'),
]

