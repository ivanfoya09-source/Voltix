from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from store.models import Product
from .models import CartItem


@receiver(user_logged_in)
def merge_carts_on_login(sender, request, user, **kwargs):
    session_cart = request.session.get(
        settings.CART_SESSION_ID, {}
    )

    if not isinstance(session_cart, dict):
        return

    if not session_cart:
        return

    guest_items = {}

    for product_id, item in session_cart.items():
        try:
            product_id = int(product_id)
            quantity = item["quantity"]
        except (ValueError, TypeError, KeyError):
            continue

        if (
            not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or quantity <= 0
        ):
            continue

        guest_items[product_id] = quantity

    with transaction.atomic():

        get_user_model().objects.select_for_update().get(
            pk=user.pk
        )

        products = Product.objects.filter(
            id__in=guest_items.keys(),
            available=True,
            stock__gt=0,
        )

        for product in products:
            guest_quantity = guest_items[product.id]

            item, created = CartItem.objects.get_or_create(
                user=user,
                product=product,
                defaults={
                    "quantity": min(
                        guest_quantity,
                        product.stock
                    )
                }
            )

            if not created:
                item.quantity = min(
                    item.quantity + guest_quantity,
                    product.stock
                )

                item.save(update_fields=[
                    "quantity",
                    "updated_at",
                ])

    request.session.pop(
        settings.CART_SESSION_ID, None
    )

    request.session.modified = True
