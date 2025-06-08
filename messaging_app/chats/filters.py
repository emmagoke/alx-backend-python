from django_filters import rest_framework as filters

from .models import Message


class MessageFilter(filters.FilterSet):
    """
    FilterSet for the Message model.
    
    Allows filtering messages by a date range on the 'sent_at' field.
    """
    # Define start_date as a filter that looks for 'sent_at' greater than or equal to the provided date.
    start_date = filters.DateTimeFilter(field_name="sent_at", lookup_expr='gte')
    
    # Define end_date as a filter that looks for 'sent_at' less than or equal to the provided date.
    end_date = filters.DateTimeFilter(field_name="sent_at", lookup_expr='lte')

    class Meta:
        model = Message
        fields = {
            'conversation': ['exact'], # Allow exact filtering by conversation ID
            'is_read': ['exact'],     # Allow filtering by read status
        }
