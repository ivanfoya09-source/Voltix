from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Order, OrderStatusHistory


class OrderStatusError(Exception):
    """Помилка зміни статусу замовлення."""
    pass


# Дозволені переходи між статусами
ALLOWED_STATUS_TRANSITIONS = {
    Order.Status.PENDING: [
        Order.Status.PROCESSING,
    ],

    Order.Status.PROCESSING: [
        Order.Status.SHIPPED,
    ],

    Order.Status.SHIPPED: [
        Order.Status.DELIVERED,
    ],

    Order.Status.DELIVERED: [],
    Order.Status.CANCELLED: [],
}


def change_order_status(
    order_id,
    new_status,
    changed_by=None,
    note=""
):

    from .emails import send_order_status_email

    with transaction.atomic():

        order = Order.objects.select_for_update().get(
            pk=order_id
        )

        old_status = order.status

        allowed = ALLOWED_STATUS_TRANSITIONS.get(
            old_status,
            []
        )

        if new_status not in allowed:
            raise OrderStatusError(
                "Неможливо змінити статус "
                f"з «{order.get_status_display()}» "
                f"на «{new_status}»."
            )

        update_data = {
            "status": new_status,
            "updated_at": timezone.now(),
        }

        if new_status == Order.Status.SHIPPED:
            update_data["estimated_delivery_date"] = (
                timezone.localdate() + timedelta(days=3)
            )

        updated = Order.objects.filter(
            pk=order.pk,
            status=old_status,
        ).update(**update_data)

        if updated != 1:
            raise OrderStatusError(
                "Статус замовлення вже змінився. "
                "Оновіть сторінку."
            )

        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            note=note or "Статус замовлення оновлено.",
        )

        transaction.on_commit(
            lambda pk=order.pk, status=new_status:
                send_order_status_email(pk, status)
        )

    order.refresh_from_db()

    return order




# СКАСУВАННЯ ЗАМОВЛЕННЯ
def cancel_order(order_id, user):
    from .emails import send_order_status_email

    with transaction.atomic():
        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=order_id,
                user=user,
            )
        )

        now = timezone.now()

        if now > order.created_at + timedelta(hours=24):
            raise OrderStatusError(
                "Минуло більше 24 годин після оформлення."
            )

        allowed_statuses = [
            Order.Status.PENDING,
            Order.Status.PROCESSING,
        ]

        if order.status not in allowed_statuses:
            raise OrderStatusError(
                "Це замовлення вже не можна скасувати."
            )

        old_status = order.status

        updated = Order.objects.filter(
            pk=order.pk,
            user=user,
            status=old_status,
            created_at__gte=now - timedelta(hours=24),
        ).update(
            status=Order.Status.CANCELLED,
            updated_at=now,
            estimated_delivery_date=None,
        )

        if updated != 1:
            raise OrderStatusError(
                "Статус уже змінився. Оновіть сторінку."
            )

        for item in order.items.all():
            if item.product_id:
                from store.models import Product

                Product.objects.filter(
                    pk=item.product_id
                ).update(
                    stock=F("stock") + item.quantity
                )

        if order.coupon_id:
            from .models import Coupon

            Coupon.objects.filter(
                pk=order.coupon_id,
                used_count__gt=0,
            ).update(
                used_count=F("used_count") - 1
            )

        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=Order.Status.CANCELLED,
            changed_by=user,
            note="Замовлення скасовано покупцем.",
        )

        transaction.on_commit(
            lambda pk=order.pk:
                send_order_status_email(
                    pk,
                    Order.Status.CANCELLED,
                )
        )

    order.refresh_from_db()

    return order
