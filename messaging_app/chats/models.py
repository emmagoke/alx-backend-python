from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
)
import uuid

# Create your models here.

class BaseUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Timestamp(models.Model):
    """
    Timestamp mixin to inherit
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    """
    Custom user model that extends Django's AbstractUser.
    This allows for additional fields or methods in the future.
    AbstractUser already includes fields:
      username, password, email, first_name,
      last_name, date_joined, last_login,
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    ROLE_GUEST = 'guest'
    ROLE_HOST = 'host'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_GUEST, 'Guest'),
        (ROLE_HOST, 'Host'),
        (ROLE_ADMIN, 'Admin'),
    ]

    # The 'email', 'first_name', 'last_name', 'password' (hashed)
    # are already part of AbstractUser.
    # 'username' is also part of AbstractUser and is typically used for login.

    # phone_number from DBML Users table
    phone_number = models.CharField(
        max_length=20,  # Adjust max_length as needed
        blank=True,     # Corresponds to [null] in DBML
        null=True,
        verbose_name="Phone Number"
        unique=True,  # Assuming phone numbers are unique
    )

    # role from DBML Users table
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default=ROLE_GUEST,
        verbose_name="Role"
    )
    # You can add additional fields here if needed
    def __str__(self):
        return self.username


class Conversation(Timestamp):
    """
    Represents a conversation involving a set of users.
    In a system with direct sender/recipient messages (as per DBML),
    a Conversation can group participants for a chat thread.
    Messages are not directly foreign-keyed to this model if following the DBML message table strictly.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        verbose_name="Participants"
    )
    # The 'created_at' and 'updated_at' fields are inherited from Timestamp mixin.

    def __str__(self):
        participant_names = ", ".join([user.username for user in self.participants.all()[:3]])
        # Add ellipsis if there are more than 3 participants
        if self.participants.count() > 3:
            participant_names += "..."
        if not participant_names:
            return f"Conversation (ID: {self.pk})"
        return f"Conversation involving {participant_names}"

    class Meta:
        ordering = ['-updated_at']
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"

class Message(models.Model):
    """
    Represents a single message sent from one user to another.
    This model is based on the DBML 'message' table structure.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # sender_id from DBML
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    # recipient_id from DBML
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
    )

    # Link directly to the Conversation
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages', # This allows Conversation.messages.all()
        verbose_name="Conversation"
    )

    # message_body text from DBML
    content = models.TextField(
        verbose_name="Content"
    )

    sent_at = models.DateTimeField(auto_now_add=True)
    
    # is_read indicates if the message has been read by recipients
    # This might need more complex logic for group chats
    # (e.g., a ManyToManyField to track read status per user)
    # For simplicity, a boolean field is used here.
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['sent_at'] # Order messages by when they were sent
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        indexes = [
            models.Index(fields=['sent_at']), # Supports default ordering and range queries
            # The FK 'conversation' already gets an index. If you also query
            # often by 'sender' AND 'timestamp' together, you could consider:
            # models.Index(fields=['sender', 'timestamp']),
        ]
