from rest_framework import serializers

from .models import Message, Conversation, User


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer, reflecting UUID primary key and other fields.
    """
    class Meta:
        model = User
        fields = (
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number',
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Reflects direct link to Conversation and UUID keys.
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(
        source="sender", write_only=True, required=True
    )
    conversation_id = serializers.UUIDField(
        source="conversation", write_only=True, required=True
    )

    class Meta:
        model = Message
        fields = (
            'message_id',     # Primary key
            'sender',         # For reading sender object
            'sender_id',      # For writing sender UUID
            'conversation',   # For reading conversation_id (default DRF behavior for FK)
            'conversation_id',# For writing conversation UUID
            'content',
            'sent_at',
            'is_read'
        )
        read_only_fields = ('message_id', 'sent_at', 'sender', 'conversation')


class ChatConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Conversation model.
    Includes participants and latest message. Reflects UUID keys.
    """
    participants = UserSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        source='participants', # This will set the participants field on the model
        write_only=True,
        label="Participant User IDs"
    )
    latest_message = ChatMessageSerializer(read_only=True) # Use the new ChatMessageSerializer

    class Meta:
        model = Conversation
        fields = (
            'conversation_id',      # Primary key
            'participants',         # For reading participant objects
            'participant_ids',      # For writing/updating participant UUIDs
            'created_at',
            'updated_at',
            'latest_message',
        )
        read_only_fields = ('conversation_id', 'created_at', 'updated_at', 'latest_message')
