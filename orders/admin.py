from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms

from .models import (
    ShippingAddress,
    Coupon,
    Order,
    OrderItem,
    OrderStatusHistory,
)

from django.contrib import messages
from django.contrib.admin import action

from .status_services import (
    OrderStatusError,
    change_order_status,
)


# АДРЕСИ ДОСТАВКИ
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "city",
        "phone",
        "is_default",
    )

    list_filter = ("city", "is_default")

    search_fields = (
        "full_name",
        "user__username",
        "phone",
        "city",
    )


# ПРОМОКОДИ
class CouponAdminForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        valid_from = cleaned_data.get("valid_from")
        valid_until = cleaned_data.get("valid_until")
        used_count = cleaned_data.get("used_count")
        max_uses = cleaned_data.get("max_uses")

        if valid_from and valid_until:
            if valid_until <= valid_from:
                raise ValidationError(
                    "Дата завершення має бути пізніше початку."
                )

        if (
            used_count is not None
            and max_uses is not None
            and used_count > max_uses
        ):
            raise ValidationError(
                "Кількість використань перевищує ліміт."
            )

        return cleaned_data


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    form = CouponAdminForm

    list_display = (
        "code",
        "discount_percent",
        "valid_from",
        "valid_until",
        "used_count",
        "max_uses",
        "is_active",
        "coupon_valid",
    )

    list_filter = ("is_active",)

    search_fields = ("code",)

    readonly_fields = ("used_count", "created_at")

    @admin.display(
        boolean=True,
        description="Дійсний"
    )
    def coupon_valid(self, obj):
        return obj.is_valid


# ТОВАРИ ЗАМОВЛЕННЯ
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

    fields = (
        "product_name",
        "price",
        "quantity",
        "line_total",
    )

    readonly_fields = fields

    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Сума")
    def line_total(self, obj):
        if not obj.pk:
            return "—"
        return f"{obj.get_total_price} ₴"



# ІСТОРІЯ СТАТУСІВ
class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0

    fields = (
        "old_status",
        "new_status",
        "changed_by",
        "note",
        "created_at",
    )

    readonly_fields = fields

    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ЗАМОВЛЕННЯ
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "email",
        "total",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "id",
        "full_name",
        "email",
        "phone",
    )

    readonly_fields = (
        "user",
        "full_name",
        "email",
        "phone",
        "city",
        "address",
        "postal_code",
        "shipping_address",
        "coupon",
        "discount_percent",
        "subtotal",
        "discount_amount",
        "total",
        "status",
        "estimated_delivery_date",
        "created_at",
        "updated_at",
    )


    # =====================================
    # ACTIONS — ЗМІНА СТАТУСІВ
    # =====================================

    actions = [
        "mark_processing",
        "mark_shipped",
        "mark_delivered",
    ]

    def _change_selected_status(
        self,
        request,
        queryset,
        target_status
    ):
        success_count = 0
        error_count = 0

        for order in queryset:

            try:
                change_order_status(
                    order_id=order.pk,
                    new_status=target_status,
                    changed_by=request.user,
                    note=(
                        "Статус змінено адміністратором "
                        "через Django Admin."
                    ),
                )

                success_count += 1

            except OrderStatusError as error:
                error_count += 1

                self.message_user(
                    request,
                    f"Замовлення №{order.pk}: {error}",
                    level=messages.WARNING,
                )

        if success_count:
            self.message_user(
                request,
                f"Успішно оновлено замовлень: {success_count}.",
                level=messages.SUCCESS,
            )

        if error_count:
            self.message_user(
                request,
                f"Пропущено замовлень: {error_count}.",
                level=messages.WARNING,
            )

    @action(
        description="📦 Позначити як «Обробляється»",
        permissions=["change"],
    )
    def mark_processing(self, request, queryset):
        self._change_selected_status(
            request,
            queryset,
            Order.Status.PROCESSING,
        )

    @action(
        description="🚚 Позначити як «Відправлено»",
        permissions=["change"],
    )
    def mark_shipped(self, request, queryset):
        self._change_selected_status(
            request,
            queryset,
            Order.Status.SHIPPED,
        )

    @action(
        description="✅ Позначити як «Доставлено»",
        permissions=["change"],
    )
    def mark_delivered(self, request, queryset):
        self._change_selected_status(
            request,
            queryset,
            Order.Status.DELIVERED,
        )


    inlines = (
        OrderItemInline,
        OrderStatusHistoryInline,
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
