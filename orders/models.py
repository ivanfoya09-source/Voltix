from decimal import Decimal

from django.conf import settings
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
)
from django.db import models
from django.utils import timezone

import uuid


# 1. АДРЕСА ДОСТАВКИ
class ShippingAddress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shipping_addresses",
        verbose_name="Користувач",
    )

    full_name = models.CharField(
        max_length=150,
        verbose_name="ПІБ отримувача",
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
    )

    city = models.CharField(
        max_length=100,
        verbose_name="Місто",
    )

    address = models.CharField(
        max_length=255,
        verbose_name="Адреса доставки",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Поштовий індекс",
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="Основна адреса",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Адреса доставки"
        verbose_name_plural = "Адреси доставки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.city}"


# 2. ПРОМОКОДИ
class Coupon(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Промокод",
    )

    discount_percent = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        verbose_name="Знижка (%)",
    )

    valid_from = models.DateTimeField(
        verbose_name="Початок дії",
    )

    valid_until = models.DateTimeField(
        verbose_name="Кінець дії",
    )

    max_uses = models.PositiveIntegerField(
        default=100,
        verbose_name="Максимальна кількість використань",
    )

    used_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Кількість використань",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активний",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоди"

    def __str__(self):
        return f"{self.code} (-{self.discount_percent}%)"

    @property
    def is_valid(self):
        now = timezone.now()

        return (
            self.is_active
            and self.valid_from <= now <= self.valid_until
            and self.used_count < self.max_uses
        )


# 3. ЗАМОВЛЕННЯ
class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Очікує підтвердження"
        PROCESSING = "processing", "Обробляється"
        SHIPPED = "shipped", "Відправлено"
        DELIVERED = "delivered", "Доставлено"
        CANCELLED = "cancelled", "Скасовано"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Покупець",
    )

    # Контактні дані
    full_name = models.CharField(
        max_length=150,
        verbose_name="ПІБ отримувача",
    )

    email = models.EmailField(
        verbose_name="Email",
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Телефон",
    )

    # адреса на момент замовлення
    city = models.CharField(
        max_length=100,
        verbose_name="Місто",
    )

    address = models.CharField(
        max_length=255,
        verbose_name="Адреса доставки",
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Поштовий індекс",
    )

    shipping_address = models.ForeignKey(
        ShippingAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Збережена адреса",
    )

    # Промокод
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="Промокод",
    )

    discount_percent = models.PositiveIntegerField(
        default=0,
        verbose_name="Знижка (%)",
    )


    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Сума товарів",
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Сума знижки",
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Підсумкова сума",
    )

    # Стан замовлення
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Статус",
    )

    estimated_delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Очікувана дата доставки",
    )

    checkout_token = models.UUIDField(
    null=True,
    blank=True,
    unique=True,
    editable=False,
    verbose_name="Ідентифікатор оформлення",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Дата створення",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Оновлено",
    )

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Замовлення №{self.pk} — {self.full_name}"

    @property
    def can_cancel(self):
        from datetime import timedelta

        return (
            self.status in [
                self.Status.PENDING,
                self.Status.PROCESSING,
            ]
            and self.created_at is not None
            and timezone.now()
            <= self.created_at + timedelta(hours=24)
        )


# 4. ТОВАРИ У ЗАМОВЛЕННІ
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Замовлення",
    )

    product = models.ForeignKey(
        "store.Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        verbose_name="Товар",
    )

    product_name = models.CharField(
        max_length=255,
        verbose_name="Назва товару на момент покупки",
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Ціна за одиницю",
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Кількість",
    )

    class Meta:
        verbose_name = "Товар замовлення"
        verbose_name_plural = "Товари замовлення"

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    @property
    def get_total_price(self):
        return self.price * self.quantity



# 5. ІСТОРІЯ СТАТУСІВ
class OrderStatusHistory(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
        verbose_name="Замовлення",
    )

    old_status = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Попередній статус",
    )

    new_status = models.CharField(
        max_length=20,
        choices=Order.Status.choices,
        verbose_name="Новий статус",
    )

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Хто змінив",
    )

    note = models.TextField(
        blank=True,
        verbose_name="Коментар",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата зміни",
    )

    class Meta:
        verbose_name = "Історія статусу"
        verbose_name_plural = "Історія статусів"
        ordering = ["created_at", "pk"]

    def __str__(self):
        return (
            f"Замовлення №{self.order_id}: "
            f"{self.get_new_status_display()}"
        )
