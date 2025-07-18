from rest_framework import serializers
from .models import User, Message, Conversation

class UserSerializer(serializers.ModelSerializer):
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone_number = serializers.CharField()
    
    class Meta:
        model = User
        fields = ["user_id", 'email', 'first_name', 'last_name', 'phone_number']
        read_only_fields = ['user_id']
        
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ["message_id", 'sender', 'message_body', 'conversation', 'sent_at']
        read_only_fields = ['messsage_id', 'sent_at']
        
class ConversationSerializer(serializers.ModelSerializer):
    messages = serializers.SerializerMethodField()
    participants = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ["conversation_id", 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']
        
    def get_messages(self,obj):
        messages = obj.messages.all()
        return MessageSerializer(messages, many=True).data
    
    def validate(self, data):
        if not data.get("participants"):
            raise serializers.ValidationError("Conversation must have at least one participant")
        return data