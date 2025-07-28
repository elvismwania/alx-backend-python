

from rest_framework import serializers
from .models import User, Conversation, Message


# User Serializer

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()  # ✔️ SerializerMethodField
    username = serializers.CharField()  # ✔️ CharField explicitly declared

    class Meta:
        model = User
        fields = [
            'user_id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'profile_photo',
            'is_online',
            'full_name',
            'bio',
            'date_joined',
            'avatar',
            'last_login',
            'is_active',
            
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


# Message Serializer

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.SerializerMethodField()
    message_body = serializers.CharField()

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'sender_username',
            'message_body',
            'sent_at',
            'is_read',
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender', 'sender_username']

    def get_sender_username(self, obj):
        return obj.sender.username
        

# Conversation Serializer

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    title = serializers.CharField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'title',
            'participants',
            'messages',
            'created_at',
        ]
        read_only_fields = ['conversation_id', 'created_at']

    # Example ValidationError usage
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return value
