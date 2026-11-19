from django.contrib import admin

from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "product",
        "quantity",
        "total_price",
        "updated_at",
    )

    list_filter = ("updated_at",)

    search_fields = (
        "user__username",
        "product__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "product",
    )
