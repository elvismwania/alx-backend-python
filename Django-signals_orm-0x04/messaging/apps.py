# Django-signals_orm-0x04/messaging/apps.py

from django.apps import AppConfig

class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    verbose_name = "Messaging System"

    def ready(self):
        # Import signals here to ensure they are connected when the app is ready
        import messaging.signals
