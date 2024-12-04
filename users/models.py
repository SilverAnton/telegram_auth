from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    telegram_chat_id = models.CharField(
        max_length=155, unique=True, verbose_name="Telegram Chat ID"
    )
    token = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, verbose_name="Token"
    )
    first_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="First Name"
    )
    last_name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name="Last Name"
    )
    username = models.CharField(
       unique=True, max_length=50, null=True, blank=True, verbose_name="Telegram Username"
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []
    def __str__(self):
        return self.username or str(self.telegram_chat_id)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
