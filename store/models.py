from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils.text import slugify
from unidecode import unidecode


class Category(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Назва категорії"
    )

    slug = models.SlugField(
        max_length=150,
        unique=True,
        allow_unicode=True,
        verbose_name="URL категорії"
    )

    description = models.TextField(
        blank=True,
        verbose_name="Опис категорії"
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Батьківська категорія"
    )

    def get_children(self):
        return self.children.all()

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ["name"]

    def __str__(self):
        return self.name



class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        verbose_name="Категорія"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Назва товару"
    )

    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        allow_unicode=True,
        verbose_name="URL товару"
    )

    description = models.TextField(
        verbose_name="Опис товару"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00"))
        ],
        verbose_name="Ціна (грн)"
    )

    stock = models.PositiveIntegerField(
        default=0,
        verbose_name="Кількість на складі"
    )

    available = models.BooleanField(
        default=True,
        verbose_name="Активний товар"
    )

    is_featured = models.BooleanField(
        default=False,
        verbose_name="Хіт продажів"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата створення"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата оновлення"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode(self.name))

            if not base_slug:
                base_slug = "product"

            base_slug = base_slug[:240].rstrip("-")
            unique_slug = base_slug
            counter = 2

            while Product.objects.filter(
                slug=unique_slug
            ).exclude(pk=self.pk).exists():
                suffix = f"-{counter}"
                unique_slug = (
                    base_slug[:255 - len(suffix)].rstrip("-")
                    + suffix
                )
                counter += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)



class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Товар"
    )

    image = models.ImageField(
        upload_to="products/",
        verbose_name="Зображення"
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Опис зображення"
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name="Головне зображення"
    )

    class Meta:
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return f"Фото: {self.product.name}"
