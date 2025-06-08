from rest_framework import permissions

from .models import Conversation


class IsParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to access it.
    """
    message = "You must be a participant in this conversation to access it."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        conversation_id = None
        if 'conversation_id' in request.query_params:
            conversation_id = request.query_params['conversation_id']
        
        if not conversation_id:
            # If no conversation_id is provided, the will view handle the
            # "Bad Request" error.
            return True
        
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
            return request.user in conversation.participants.all()
        except (Conversation.DoesNotExist, ValueError, TypeError):
            return False


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to interact with it.
    
    This permission is designed to check for:
    - Listing messages in a conversation (GET)
    - Creating a message in a conversation (POST)
    - Retrieving, updating, or deleting a specific message (GET, PUT, PATCH, DELETE)
    """
    def has_permisssion(self, request, view):
        """
        Checks permission for list and create actions.
        It determines the conversation from the request's query parameters or body.
        """
        conversation_id = None

        # For listing messages (e.g., GET /api/messages/?conversation_id=...)
        if 'conversation_id' in request.query_params:
            conversation_id = request.query_params["conversation_id"]
        # For creating a message (e.g., POST /api/messages/)
        elif 'conversation_id' in request.data:
            conversation_id = request.data["conversation_id"]
        
        if not conversation_id:
            # If no conversation is specified, we can't check permissions.
            # We let the request proceed to the view, which should handle the
            # missing ID as a bad request.
            return True
        
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
            # The core check: is the requesting user in the conversation's participants?
            return request.user in conversation.participants.all()
        except Conversation.DoesNotExist:
            # If the conversation doesn't exist, deny permission.
            return False
    
    def has_object_permission(self, request, view, obj):
        """
        Checks permission for detail actions (retrieve, update, delete a specific message).
        The 'obj' here is the Message instance.
        """
        # For a message object, we check the participants of its parent conversation.
        return request.user in obj.conversation.participants.all()
