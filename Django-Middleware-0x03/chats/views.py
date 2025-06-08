from rest_framework import viewsets, status
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.db.models import Prefetch
import uuid
from django.shortcuts import get_object_or_404
from rest_framework import filters

from .permissions import IsParticipantOfConversation


from .models import Conversation, Message, User
from .serializers import (
    ChatConversationSerializer, ChatMessageSerializer, UserSerializer
)
from .pagination import MessagePagination
from .filters import MessageFilter
# Create your views here.


class UserViewSet(viewsets.ViewSet):
    """
    A ViewSet for listing and creating users with explicit action implementations.

    - `list`: Lists all users. Requires admin privileges.
    - `create`: Creates a new user. Open to anyone for registration.
    - `retrieve`: Retrieves a single user's details. Requires admin privileges.
    """
    # In a basic ViewSet, queryset is not used automatically, but it's good practice
    # to have it for reference and for other tools that inspect the view.
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        This permission logic remains exactly the same as the ModelViewSet version.
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        
        return [permission() for permission in permission_classes]

    def list(self, request):
        """
        Handles GET requests to list all users.
        """
        queryset = User.objects.all().order_by('-date_joined')
        # We pass the queryset to the serializer, specifying many=True for a list.
        serializer = self.serializer_class(queryset, many=True)
        return Response({
            "data": serializer.data,
            "message": "List of all users",
            },
        )

    def create(self, request):
        """
        Handles POST requests to create a new user.
        """
        # We pass the incoming request data to the serializer.
        serializer = self.serializer_class(data=request.data)
        
        # Validate the data. If it's invalid, this will raise an exception.
        serializer.is_valid(raise_exception=True)
        
        # If valid, the .save() method will trigger the serializer's .create() method,
        # which correctly handles hashing the password.
        serializer.save()
        
        # Return the new user's data with a 201 CREATED status.
        return Response(
            {
                "data": serializer.data,
                "message": "User created successfully",
            }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        Handles GET requests for a single user instance.
        """
        queryset = User.objects.all()
        # Retrieve the specific user by their primary key (pk), or return a 404 error.
        user = get_object_or_404(queryset, pk=pk)
        # Serialize the single user object.
        serializer = self.serializer_class(user)
        return Response(serializer.data)


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
    filter_backends = [filters.OrderingFilter, MessageFilter]
    pagination_class = MessagePagination

    def get_serializer_context(self):
        """
        Pass request object to serializer context.
        """
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}
    
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        # print(self.__dict__)
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

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
        conversation_id_str = request.query_params.get('conversation_id')

        if not conversation_id_str:
            return Response(
                {"error": "conversation_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST)

        # The permission class already handles checking if the user can access this.
        # We can safely filter the messages.
        queryset = Message.objects.filter(
            conversation_id=conversation_id_str
        ).select_related('sender').order_by('-sent_at') # Order by -sent_at for latest first

        # 1. Manually paginate the queryset
        page = self.paginator.paginate_queryset(queryset, request, view=self)

        # 2. If paginate_queryset returns a page, serialize and return it
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            # Use the paginator's get_paginated_response method to build the final response
            return self.paginator.get_paginated_response(serializer.data)

        # 3. If pagination is not enabled, serialize the whole queryset
        serializer = self.serializer_class(queryset, many=True)
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
