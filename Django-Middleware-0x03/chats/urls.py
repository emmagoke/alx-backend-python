from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    ConversationViewSet,
    MessageViewSet,
    UserViewSet
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')


urlpatterns = [
    path('', include(router.urls)),
    path("auth/login/", TokenObtainPairView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]


# Example API Endpoints generated:
# Top-level Conversations:
# - GET /conversations/ (List conversations for the user)
# - POST /conversations/ (Create a new conversation)
# - GET /conversations/{conversation_pk}/ (Retrieve a specific conversation)
# - ... other ModelViewSet actions for ConversationViewSet if it were a ModelViewSet

# Nested Messages (linked to a specific conversation):
# - GET /conversations/{conversation_pk}/messages/ (List messages for that conversation)
# - POST /conversations/{conversation_pk}/messages/ (Create a new message in that conversation)
# - GET /conversations/{conversation_pk}/messages/{message_pk}/ (Retrieve a specific message)
# - ... other ModelViewSet actions for MessageViewSet if it were a ModelViewSet

# Note: Since you are using viewsets.ViewSet, you'll need to ensure your MessageViewSet's
# list and create methods can handle the `conversation_pk` from the URL if you want to
# automatically scope messages to the conversation from the URL.
# The current MessageViewSet.list method expects `conversation_id` as a query parameter.
# To use the nested URL's `conversation_pk`, you'd access `self.kwargs['conversation_pk']`
# in the MessageViewSet's methods.
