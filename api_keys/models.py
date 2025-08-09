import uuid

from django.conf import settings
from django.db import models


class APIKey(models.Model):
    """
    A model to store and manage API keys for users.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="api_keys",
    )
    name = models.CharField(
        max_length=100,
        help_text="A descriptive name for the API key",
    )
    key = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="The unique API key",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # return the first 8 chars of key for display purposes
        return f"{self.name} ({str(self.key)[:8]}...)"

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"
        ordering = ["-created_at"]
