# Django-signals_orm-0x04/myproject/settings.py (example)

# ... (rest of your settings.py content) ...

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'messaging', # Ensure this is present
]

# ... (other settings like MIDDLEWARE, TEMPLATES, DATABASES, AUTH_PASSWORD_VALIDATORS) ...

# Task 5: CACHES configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake', # A unique string for this cache instance
    }
}

# Add LOGIN_URL and LOGIN_REDIRECT_URL for the @login_required decorator to work
LOGIN_URL = '/admin/login/' # Or your custom login URL if you have one
LOGIN_REDIRECT_URL = '/messaging/inbox/' # Redirect to inbox after login

# For logout to work, you might need a logout view and URL
# Example: from django.contrib.auth import views as auth_views
# urlpatterns = [
#     ...
#     path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
# ]

