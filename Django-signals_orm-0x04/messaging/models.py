from django.db import models
from django.contrib.auth.models import (
    AbstractUser,
)
import uuid

# Create your models here.


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
    # ROLE_GUEST = 'guest'
    # ROLE_HOST = 'host'
    # ROLE_ADMIN = 'admin'
    # ROLE_CHOICES = [
    #     (ROLE_GUEST, 'Guest'),
    #     (ROLE_HOST, 'Host'),
    #     (ROLE_ADMIN, 'Admin'),
    # ]

    # The 'email', 'first_name', 'last_name', 'password' (hashed)
    # are already part of AbstractUser.
    # 'username' is also part of AbstractUser and is typically used for login.

    # phone_number from DBML Users table
    phone_number = models.CharField(
        max_length=20,  # Adjust max_length as needed
        blank=True,     # Corresponds to [null] in DBML
        null=True,
        unique=True,  # Assuming phone numbers are unique
    )

    # role from DBML Users table
    # role = models.CharField(
    #     max_length=10,
    #     choices=ROLE_CHOICES,
    #     default=ROLE_GUEST,
    #     verbose_name="Role"
    # )
    # You can add additional fields here if needed
    def __str__(self):
        return self.username


class Message(models.Model):
    """
    Represents a direct message sent from one user to another.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', help_text="The user who sent the message.")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', help_text="The user who will receive the message.")
    content = models.TextField(help_text="The text content of the message.")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="The date and time the message was created.")
    is_read = models.BooleanField(default=False, help_text="Indicates whether the receiver has read the message.")

    def __str__(self):
        """
        Returns a string representation of the message, useful for the admin interface.
        """
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"


class Notification(models.Model):
    """
    Represents a notification for a user, typically triggered by an event like a new message.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', help_text="The user who receives the notification.")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, help_text="The message that this notification is about.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="The date and time the notification was created.")
    is_seen = models.BooleanField(default=False, help_text="Indicates whether the user has seen the notification.")

    def __str__(self):
        """
        Returns a string representation of the notification.
        """
        return f"Notification for {self.user.username} regarding message from {self.message.sender.username}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
