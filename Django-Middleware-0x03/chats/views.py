from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from .permissions import IsParticipantOfConversation
from rest_framework.response import Response
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer
from .models import User, Message, Conversation
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import MessageFilter
from .pagination import MessagePagination


# Create your views here.


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    pagination_class = MessagePagination

    def get_queryset(self):
        """
        This view is nested under a conversation.
        It should only return messages that belong to the conversation
        specified in the URL.
        """
        # The 'conversation_pk' comes from the URL, thanks to the nested router.
        conversation_pk = self.kwargs.get('conversation_pk')

        # Filter messages to only include those from the specified conversation.
        return Message.objects.filter(conversation_id=conversation_pk)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if request.user not in message.conversation.participants.all():
            return Response({'detail': 'Not authorized.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]

    def get_queryset(self):
        """
        This view is nested under a user, so we must filter conversations
        based on the user_pk from the URL.
        """
        # self.kwargs contains the captured keyword arguments from the URL router.
        user_pk = self.kwargs.get('user_pk')

        if user_pk:
            # Return only conversations where the user from the URL is a participant.
            return Conversation.objects.filter(participants__user_id=user_pk)

        # As a safe default for a nested viewset, return an empty queryset
        # if the user_pk is not in the URL for some reason.
        return Conversation.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None, user_pk=None):
        conversation = self.get_object()
        data = request.data.copy()
        data['conversation_id'] = conversation.conversation_id
        data['sender_id'] = request.user.user_id
        serializer = MessageSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Respnose(serializer.data, status=status.HTTP_201_CREATED)
