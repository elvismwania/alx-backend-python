from django.contrib import admin

# Register your models here.

from .models import Message, Notification

admin.site.register(Message)
admin.site.register(Notification)
