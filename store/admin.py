
from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "parent",
    )

    list_filter = ("parent",)

    search_fields = ("name",)

    prepopulated_fields = {
        "slug": ("name",)
    }


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt_text", "is_main")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "available",
        "is_featured",
        "created_at",
    )

    list_filter = (
        "category",
        "available",
        "is_featured",
        "created_at",
    )

    search_fields = ("name", "description")

    list_editable = ("price", "stock", "available", "is_featured")

    list_per_page = 20

    inlines = [ProductImageInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_main")
    list_filter = ("is_main",)
    search_fields = ("product__name",)


admin.site.site_header = "VOLTIX — Адміністрування"
admin.site.site_title = "VOLTIX Admin"
admin.site.index_title = "Керування інтернет-магазином"
