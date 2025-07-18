from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets,status, filters
from .models import User, Conversation, Message
from .serializers import  ConversationSerializer,MessageSerializer

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for listing and creating conversations
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    def create(self,request,*args,**kwargs):
        """
        Create a new conversation with participants.
        """
        participants = request.data.get("participants", [])
        if not participants:
            return Response(
                {"error":"Participatants field is required"},
                status = status.HTTP_400_BAD_REQUEST
            )
        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()
        
        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer(read_only=True)
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['message_body']
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']
    
    """
    ViewSet for listing and creating messages
    """
    
    def create(self,request,*args,**kwargs):
        """
        Send a message to an existing conversation.
        """
        conversation_id = request.data.get("conversation")
        message_body = request.data.get("message_body")
        sender = request.data.get("sender")
        
        if not (conversation_id and message_body and sender):
            return Response(
                {"error":"conversation_id, message_body and sender fields are required"},
                status = status.HTTP_400_BAD_REQUEST
            )
        
        message = Message.objects.create(
            conversation_id = conversation_id,
            message_body = message_body,
            sender = sender
        )
        
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
