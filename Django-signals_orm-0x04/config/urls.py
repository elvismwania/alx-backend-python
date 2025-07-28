"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from chats import auth as chat_auth



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('chats.urls')), # Include the main app's URLs
    path('api-auth/', include('rest_framework.urls')), # This line enables the browsable API for authentication # Enable DRF’s browsable login/logout UI
    path('api/v1/token', chat_auth.TokenObtainPairView.as_view(), name='token_obtain_pair'), # login
    path('api/v1/token/refresh', chat_auth.TokenRefreshView.as_view(), name='token_refersh'), # refersh
    
]
