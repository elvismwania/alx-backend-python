from django.urls import path, include
from rest_framework_nested import routers

from .views import UserViewSet, ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')

user_conversations_router = routers.NestedDefaultRouter(
    router, r'users', lookup='user')
user_conversations_router.register(
    r'conversations', ConversationViewSet, basename='user-conversations')

conversation_messages_router = routers.NestedDefaultRouter(
    router, r'conversations', lookup='conversation')
conversation_messages_router.register(
    r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(user_conversations_router.urls)),
    path('', include(conversation_messages_router.urls)),
]
