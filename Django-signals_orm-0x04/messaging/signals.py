from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Message, Notification


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    A signal that triggers when a new Message instance is created.

    This function creates a Notification object for the receiver of the message.
    The 'created' flag ensures this only runs when a new message is created,
    not when an existing one is updated.
    """
    if created:
        # The instance is the Message that was just saved.
        message = instance
        
        # We want to notify the receiver of the message.
        recipient = message.receiver
        
        # Create the notification.
        Notification.objects.create(
            user=recipient,
            message=message
        )
        print(f"Notification created for user {recipient.username} for message from {message.sender.username}")
