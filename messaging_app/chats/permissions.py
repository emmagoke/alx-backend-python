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
