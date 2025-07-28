# Django-signals_orm-0x04/messaging/admin.py

from django.contrib import admin
from .models import Message, Notification

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'content', 'timestamp')
    list_filter = ('timestamp', 'sender', 'receiver')
    search_fields = ('content', 'sender__username', 'receiver__username')
    date_hierarchy = 'timestamp'
    raw_id_fields = ('sender', 'receiver') # For easier selection if many users

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp', 'user')
    search_fields = ('user__username', 'message__content')
    date_hierarchy = 'timestamp'
    raw_id_fields = ('user', 'message') # For easier selection
