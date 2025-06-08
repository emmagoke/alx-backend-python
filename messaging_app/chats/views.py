from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Prefetch
import uuid
from rest_framework import filters

from .permissions import IsParticipantOfConversation


from .models import Conversation, Message, User
from .serializers import (
    ChatConversationSerializer, ChatMessageSerializer, UserSerializer
)
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or created.
    
    - 'create': Anyone can create a new user (public registration).
    - 'list': Only admin users can list all users.
    - 'retrieve', 'update', 'partial_update', 'destroy': Only admin users.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # Allow anyone to create a new user (POST action)
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        # For all other actions (list, retrieve, etc.), require admin privileges
        else:
            permission_classes = [permissions.IsAdminUser]
        
        return [permission() for permission in permission_classes]


class ConversationViewSet(viewsets.ViewSet):
    """
    ViewSet for listing and creating conversations using viewsets.ViewSet.
    """
    serializer_class = ChatConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]

    def get_serializer_context(self):
        """
        Pass request object to serializer context.
        """
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        kwargs.setdefault('context', self.get_serializer_context())
        return self.serializer_class(*args, **kwargs)

    def list(self, request):
        """
        This view should return a list of all the conversations
        for the currently authenticated user.
        """
        user = request.user
        queryset = Conversation.objects.filter(participants=user).prefetch_related(
            Prefetch('participants', queryset=User.objects.all()),
            Prefetch('messages', queryset=Message.objects.order_by('-sent_at')) # For latest_message in serializer
        ).distinct()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "data": serializer.data,
            })

    def create(self, request):
        """
        Create a new conversation.
        The serializer's create method handles adding the current user
        to participant_ids if it's not present and context is passed.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # The ChatConversationSerializer's create method (from Canvas) handles:
        # - Adding current user to participant_ids if context has request.user
        # - Validating participant count
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ViewSet):
    """
    ViewSet for listing and sending messages using viewsets.ViewSet.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.OrderingFilter]

    def get_serializer_context(self):
        """
        Pass request object to serializer context.
        """
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        kwargs.setdefault('context', self.get_serializer_context())
        return self.serializer_class(*args, **kwargs)

    def list(self, request):
        """
        This view should return a list of messages for a given conversation ID,
        provided as a query parameter 'conversation_id'.
        The user must be a participant of the conversation.
        """
        user = request.user
        conversation_id_str = request.query_params.get('conversation_id')

        if not conversation_id_str:
            return Response({"detail": "conversation_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation_uuid = uuid.UUID(conversation_id_str)
        except ValueError:
            return Response({"detail": "Invalid conversation_id format."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the conversation exists and the user is a participant
        try:
            conversation = Conversation.objects.get(conversation_id=conversation_uuid)
            if user not in conversation.participants.all():
                raise PermissionDenied("You are not a participant in this conversation.")
        except Conversation.DoesNotExist:
            raise NotFound("Conversation not found.")
        
        queryset = Message.objects.filter(conversation=conversation).select_related(
            'sender', 'conversation' # Optimize queries
        ).order_by('sent_at')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        """
        Send a new message to an existing conversation.
        The conversation_id is expected in the request data.
        The sender is automatically set to the authenticated user by the serializer if not provided,
        or can be explicitly set here.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # For clarity, let's fetch the conversation_id from request data for permission check here.
        conversation_id_str_from_data = request.data.get('conversation_id')
        if not conversation_id_str_from_data:
             # This should be caught by serializer validation if 'conversation_id' is required.
            return Response({"conversation_id": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            conversation_uuid_for_check = uuid.UUID(str(conversation_id_str_from_data))
        except (ValueError, TypeError):
            return Response({"conversation_id": ["Invalid UUID format."]}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if the conversation exists and user is a participant
            target_conversation = Conversation.objects.get(conversation_id=conversation_uuid_for_check)
            if request.user not in target_conversation.participants.all():
                raise PermissionDenied("You do not have permission to send messages to this conversation.")
        except Conversation.DoesNotExist:
            # This error will also be caught by the serializer's create method if it tries to fetch
            # a non-existent conversation, but checking here provides an earlier response.
            raise NotFound("Target conversation not found.")

        message = serializer.save(sender=request.user)
        response_serializer = self.get_serializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
