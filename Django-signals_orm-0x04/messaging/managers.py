from django.db import models


class UnreadMessagesManager(models.Manager):
    """
    A custom manager for the Message model that provides a method to
    efficiently retrieve unread messages for a specific user.
    """
    def unread_for_user(self, user):
        """
        Returns a queryset of unread messages for the given user.
        - Uses select_related() to pre-fetch sender details.
        - Uses only() to load just the necessary fields from the database,
          improving query performance.
        """
        return self.get_queryset().filter(
            receiver=user, 
            is_read=False
        ).select_related('sender').only(
            'pk', 'content', 'timestamp', 'sender__username'
        )
