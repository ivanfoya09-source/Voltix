
from django.conf import settings
from django.db import models


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name="Користувач",
    )

    product = models.ForeignKey(
        "store.Product",
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
        verbose_name="Товар",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата додавання",
    )

    class Meta:
        verbose_name = "Обраний товар"
        verbose_name_plural = "Обрані товари"
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_wishlist_user_product",
            )
        ]

    def __str__(self):
        return f"{self.user} ❤️ {self.product.name}"
