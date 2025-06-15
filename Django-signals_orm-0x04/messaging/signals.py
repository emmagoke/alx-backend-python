from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory, User


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


@receiver(pre_save, sender=Message)
def log_message_edit_history(sender, instance, **kwargs):
    """
    A signal that triggers before a Message instance is saved.
    
    If the message is being updated and its content has changed, this function
    logs the old content to the MessageHistory model and marks the message
    as edited.
    """
    # We only care about updates, not new message creations.
    # An existing instance will have a primary key (pk).
    if instance.pk:
        try:
            # Retrieve the original message from the database
            original_message = Message.objects.get(pk=instance.pk)
            # Check if the content has been modified
            if original_message.content != instance.content:
                # Create a history record with the old content
                MessageHistory.objects.create(
                    message=original_message,
                    old_content=original_message.content,
                    edited_by=original_message.sender # Assume the sender is the editor
                )
                # Mark the instance as edited before it's saved
                instance.is_edited = True
                print(f"Message {instance.pk} edited. Old content saved to history.")
        except Message.DoesNotExist:
            # This case should not happen for an existing instance, but we handle it just in case.
            pass


@receiver(post_delete, sender=User)
def delete_user_related_data(sender, instance, **kwargs):
    """
    A signal that triggers after a User instance is deleted.

    This function cleans up any remaining data associated with the user.
    Note: Deletion of Message and Notification objects where the user is
    the sender, receiver, or recipient is handled automatically by the
    database's `ON DELETE CASCADE` behavior, as defined in the models.
    
    This signal specifically cleans up MessageHistory records where the
    deleted user was the editor, which uses `ON DELETE SET NULL`.
    """
    user = instance
    
    # Clean up MessageHistory where the deleted user was the editor.
    MessageHistory.objects.filter(edited_by=user).delete()
    
    print(f"Cleaned up all remaining data for deleted user {user.username}.")
