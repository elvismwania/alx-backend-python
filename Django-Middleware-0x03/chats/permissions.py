from rest_framework.permissions import BasePermission
from rest_framework import permissions
from .models import Message, Conversation


class IsParticipantOfConversation(BasePermission):
    """
    Custom permission to only allow participants of a conversation to access or modify messages.
    """

    def has_permission(self, request, view):
        # Ensure the user is authenticated
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Read permissions (GET, HEAD, OPTIONS)
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            if isinstance(obj, Message):
                return user in obj.conversation.participants.all()
            if isinstance(obj, Conversation):
                return user in obj.participants.all()

        # Write permissions: must be participant
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if isinstance(obj, Message):
                return user in obj.conversation.participants.all()
            if isinstance(obj, Conversation):
                return user in obj.participants.all()

        return False
