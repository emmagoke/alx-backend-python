from django.urls import path, include
from rest_framework import routers

from .views import (
    ConversationViewSet,
    MessageViewSet,
)

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Create a nested router for messages within conversations
# This will create URLs like: /conversations/{conversation_pk}/messages/
conversations_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversations_router.register(r'messages', MessageViewSet, basename='conversation-messages')

# The urlpatterns list routes URLs to views.
# The `router.urls` will include routes for both the top-level conversations
# and the nested messages.
urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversations_router.urls)),
]
