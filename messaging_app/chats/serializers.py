from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import Message, Conversation, User


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer, reflecting UUID primary key and other fields.
    """
    password = serializers.CharField(
        write_only=True,  # <--- THIS IS THE KEY
        required=True,
        # style={'input_type': 'password'}
    )
    class Meta:
        model = User
        fields = (
            'user_id', 'username', 'email', 'first_name', 'last_name',
            'role', 'phone_number', 'password'
        )
        read_only_fields = ('user_id', 'role')
    
    def create(self, validated_data):
        """
        Override the default create method to handle password hashing.
        """
        # Hash the password before saving the user instance.
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)


class ChatMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.
    Reflects direct link to Conversation and UUID keys.
    """
    sender = UserSerializer(read_only=True)
    # sender_id = serializers.UUIDField(
    #     source="sender", write_only=True, required=True
    # )
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
    
    def create(self, validated_data):
        # Automatically set sender from request if not provided in payload
        # and if the serializer is initialized with request context.
        request = self.context.get('request')
        
        # Get the user from the request object using attribute access (request.user)
        request_user = request.user if request else None

        sender_uuid = validated_data.pop('sender_id', None)

        if sender_uuid: # If sender_id was passed in payload
            try:
                validated_data['sender'] = User.objects.get(user_id=sender_uuid)
            except User.DoesNotExist:
                raise serializers.ValidationError({"sender_id": "User with this ID does not exist."})
        elif request_user and request_user.is_authenticated: # If not in payload, try context
             validated_data['sender'] = request_user
        else: # If not set by context or payload, and sender is required
             raise serializers.ValidationError({"sender_id": "Sender is required and could not be determined."})

        # print("Valid: ", validated_data)
        conversation_uuid = validated_data.pop('conversation')
        try:
            validated_data['conversation'] = Conversation.objects.get(conversation_id=conversation_uuid)
        except Conversation.DoesNotExist:
            raise serializers.ValidationError({"conversation_id": "Conversation with this ID does not exist."})

        return super().create(validated_data)


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
    # latest_message = ChatMessageSerializer(read_only=True)

    display_name = serializers.CharField(source='__str__', read_only=True)
    conversation_type = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = (
            'conversation_id',      # Primary key
            'participants',         # For reading participant objects
            'participant_ids',      # For writing/updating participant UUIDs
            'created_at',
            'updated_at',
            # 'latest_message',
            'display_name',
            'conversation_type',
        )
        read_only_fields = ('conversation_id', 'created_at', 'updated_at', 'latest_message')
    
    def get_conversation_type(self, obj: Conversation):
        if obj.participants.count() == 2:
            # Check if one of the participants is the current user (if context is available)
            # For simplicity, just returning "1-on-1"
            return "1-on-1 Chat"
        elif obj.participants.count() > 2:
            return "Group Chat"
        return "Unknown"
    
    def create(self, validated_data):
        participant_uuids = validated_data.pop('participants')
        # Ensure current user from context is added to participants if not already present
        # Safely get the request object from the context dictionary.
        request = self.context.get('request')
        
        # Get the user from the request object using attribute access (request.user)
        request_user = request.user if request else None

        if request_user and request_user.is_authenticated:
            if request_user.user_id not in participant_uuids:
                participant_uuids.append(request_user.user_id) # Add current user if not listed

        if len(participant_uuids) < 2: # Re-check after potentially adding current user
            raise serializers.ValidationError({"participant_ids": "A conversation must involve at least two distinct participants."})

        instance = Conversation.objects.create(**validated_data)
        if participant_uuids:
            participants_qs = User.objects.filter(user_id__in=participant_uuids)
            if len(participants_qs) != len(set(participant_uuids)): # Check if all provided UUIDs were valid
                raise serializers.ValidationError({"participant_ids": "One or more participant UUIDs are invalid or duplicate."})
            instance.participants.set(participants_qs)
        return instance
    
    def validate_participant_ids(self, value_list_of_uuids):
        # This validation runs when 'participant_ids' is provided in the input data
        if len(value_list_of_uuids) < 2:
            raise serializers.ValidationError("A conversation must have at least two participants.")
        
        return value_list_of_uuids
