from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class CustomUser(AbstractUser):

    class Meta:
        verbose_name = "Користувач"
        verbose_name_plural = "Користувачі"

    def __str__(self):
        return self.username


class UserProfile(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Користувач"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Номер телефону"
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Місто"
    )

    address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Адреса"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення профілю"
    )

    class Meta:
        verbose_name = "Профіль користувача"
        verbose_name_plural = "Профілі користувачів"

    def __str__(self):
        return f"Профіль: {self.user.username}"
