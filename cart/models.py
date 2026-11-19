from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator


class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Користувач"
    )

    product = models.ForeignKey(
        "store.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Кількість"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата додавання"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення"
    )

    class Meta:
        verbose_name = "Товар у кошику"
        verbose_name_plural = "Товари в кошиках"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_cart_product"
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="cart_quantity_positive"
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username}: "
            f"{self.product.name} × {self.quantity}"
        )

    @property
    def total_price(self):
        return self.product.price * self.quantity
