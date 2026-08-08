# chats/models.py

from django.db import models
from django.contrib.auth.models import User


class Chat(models.Model):
    users = models.ManyToManyField(
        User,
        related_name='chats'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        usernames = ", ".join(
            user.username for user in self.users.all()
        )
        return f"Chat between {usernames}"


class Message(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    content = models.TextField(
        blank=True,
        null=True
    )

    image = models.ImageField(
        upload_to='chat_images/',
        blank=True,
        null=True
    )

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    # Used for ✓ and ✓✓ read receipts
    is_read = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        if self.content:
            return f"{self.sender.username}: {self.content[:20]}"
        return f"{self.sender.username}: Image"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])