from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

from orders.models import Order, OrderItem


class Review(models.Model):
    # Товар, на який залишили відгук
    product = models.ForeignKey(
        "store.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Товар",
    )

    # Автор відгуку
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Покупець",
    )

    # Оцінка від 1 до 5
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        verbose_name="Оцінка",
    )

    # Заголовок
    title = models.CharField(
        max_length=150,
        verbose_name="Заголовок відгуку",
    )

    # Текст відгуку
    comment = models.TextField(
        verbose_name="Текст відгуку",
    )

    # Переваги та недоліки
    advantages = models.TextField(
        blank=True,
        verbose_name="Переваги",
    )

    disadvantages = models.TextField(
        blank=True,
        verbose_name="Недоліки",
    )

    # Модерація
    is_approved = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="Схвалено модератором",
    )

    # Дати
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата створення",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення",
    )

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_product_user_review",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="review_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} — {self.product.name} "
            f"({self.rating}/5)"
        )

    @staticmethod
    def has_purchased_product(user, product):

        if not user or not user.pk or not product or not product.pk:
            return False

        return OrderItem.objects.filter(
            order__user=user,
            order__status=Order.Status.DELIVERED,
            product=product,
        ).exists()

    def clean(self):
        super().clean()

        if (
            self._state.adding
            and self.user_id is not None
            and self.product_id is not None
        ):
            if not self.has_purchased_product(
                self.user,
                self.product,
            ):
                raise ValidationError(
                    "Залишити відгук можна лише після "
                    "отримання цього товару."
                )

        if self.title and not self.title.strip():
            raise ValidationError({
                "title": "Введіть заголовок відгуку."
            })

        if self.comment and not self.comment.strip():
            raise ValidationError({
                "comment": "Введіть текст відгуку."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
