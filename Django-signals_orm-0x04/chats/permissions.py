

from rest_framework import permissions



class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows only authenticated users who are participants of a conversation
    to access or modify related resources.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Allow safe methods (GET, HEAD, OPTIONS) for all participants
        if request.method in permissions.SAFE_METHODS:
            return self._is_participant(user, obj)

        # Restrict PUT, PATCH, DELETE only to participants
        if request.method in ["PUT", "PATCH", "DELETE"]:
            return self._is_participant(user, obj)

        # Allow POST only if participant (e.g., sending a message)
        if request.method == "POST":
            return self._is_participant(user, obj)

        return False

    def _is_participant(self, user, obj):
        if hasattr(obj, 'participants'):
            return user in obj.participants.all()
        if hasattr(obj, 'conversation'):
            return user in obj.conversation.participants.all()
        return False





"""
class IsParticipantOrSender(permissions.BasePermission):

    #Custom permission to only allow users to access their own conversations/messages.
    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(obj, 'participants'):
            return user in obj.participants.all()

        if hasattr(obj, 'sender'):
            return obj.sender == user

        return False
"""