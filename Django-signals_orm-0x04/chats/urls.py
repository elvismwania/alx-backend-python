

from django.urls import path, include
from rest_framework_nested import routers
from rest_framework.routers import DefaultRouter 
from .views import ConversationViewSet, MessageViewSet, UserViewSet



# This router will handle the main endpoints for users, conversations, and messages
router = routers.DefaultRouter()
router.register('users', UserViewSet) 
router.register('conversations', ConversationViewSet)
router.register('messages', MessageViewSet)


# This allows for nested routing under users
# and conversations, enabling endpoints like /users/{user_id}/conversations/
users_router = routers.NestedDefaultRouter(router, r'users', lookup='user') 

# Registering conversations under users
# This allows for endpoints like /users/{user_id}/conversations/
users_router.register(r'conversations', ConversationViewSet, basename='user-conversations')

# Nested router for /conversations/{conversation_id}/messages/
# This allows for nested routing under conversations
conversation_router = routers.NestedDefaultRouter(users_router, r'conversations', lookup='conversation')

# Registering messages under conversations
# This allows for endpoints like /conversations/{conversation_id}/messages/
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')


# Main urlpatterns for the app
urlpatterns = [
    
    path('', include(router.urls)),  # Main endpoints for users, conversations, and messages
    path('', include(users_router.urls)), # Nested endpoints for user conversations
    path('', include(conversation_router.urls)), # Nested endpoints for messages
    
]

urlpatterns += router.urls # This line ensures that the main router's URLs are included in the urlpatterns