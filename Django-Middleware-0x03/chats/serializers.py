from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ['user_id', 'phone_number', 'email', 'password',
                  'first_name', 'last_name', 'role', 'created_at']

    def create(self, validated_data):
        """
        Intercept the user creation process to properly handle the password.
        """
        # We manually call our model's manager, which gives us access
        # to the create_user() method we defined.
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            # Pass the password to the method that knows how to hash it.
            password=validated_data['password']
        )
        return user

    def validate(self, data):
        # Dummy validation logic
        if not data.get('email'):
            raise serializers.ValidationError("Email is required.")
        return data


class MessageSerializer(serializers.ModelSerializer):
    sent_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Message
        fields = ['message_id', 'sender_id', 'message_body', 'sent_at']


class ConversationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants',
                  'created_at', 'messages']

    def get_messages(self, obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data
