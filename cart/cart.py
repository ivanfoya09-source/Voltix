from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model

from store.models import Product
from .models import CartItem


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.user = request.user
        self.is_authenticated = self.user.is_authenticated

        if self.is_authenticated:
            # Кошик із бази даних
            items = CartItem.objects.filter(
                user=self.user
            ).values("product_id", "quantity")

            self.cart = {
                str(item["product_id"]): {
                    "quantity": item["quantity"]
                }
                for item in items
            }

        else:
            # Кошик гостя із сесії
            self.cart = self.session.get(
                settings.CART_SESSION_ID, {}
            )

    def add(
        self,
        product,
        quantity=1,
        override_quantity=False
    ):
        product_id = str(product.id)

        if not isinstance(quantity, int) or quantity < 1:
            raise ValueError("Некоректна кількість товару.")

        if self.is_authenticated:
            with transaction.atomic():

                get_user_model().objects.select_for_update().get(
                    pk=self.user.pk
                )

                item, created = CartItem.objects.get_or_create(
                    user=self.user,
                    product=product,
                    defaults={"quantity": quantity}
                )

                if not created:
                    if override_quantity:
                        item.quantity = quantity
                    else:
                        item.quantity += quantity

                    item.save(update_fields=[
                        "quantity",
                        "updated_at",
                    ])

                self.cart[product_id] = {
                    "quantity": item.quantity
                }

        else:
            if product_id not in self.cart:
                self.cart[product_id] = {"quantity": 0}

            if override_quantity:
                self.cart[product_id]["quantity"] = quantity
            else:
                self.cart[product_id]["quantity"] += quantity

            self.save()

    def remove(self, product):
        product_id = str(product.id)

        if self.is_authenticated:
            CartItem.objects.filter(
                user=self.user,
                product=product
            ).delete()

            self.cart.pop(product_id, None)

        else:
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()

    def save(self):
        if not self.is_authenticated:
            self.session[
                settings.CART_SESSION_ID
            ] = self.cart

            self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()

        products = (
            Product.objects
            .filter(id__in=product_ids)
            .select_related("category")
            .prefetch_related("images")
        )

        for product in products:
            item = self.cart[str(product.id)]
            quantity = item.get("quantity", 0)

            if (
                not isinstance(quantity, int)
                or isinstance(quantity, bool)
                or quantity <= 0
            ):
                continue

            yield {
                "product": product,
                "quantity": quantity,
                "price": product.price,
                "total_price": product.price * quantity,
            }

    def __len__(self):
        return sum(
            item["quantity"]
            for item in self.cart.values()
            if isinstance(item.get("quantity"), int)
            and not isinstance(item.get("quantity"), bool)
            and item["quantity"] > 0
        )

    def get_total_price(self):
        return sum(
            (
                item["total_price"]
                for item in self
            ),
            Decimal("0.00")
        )

    def clear(self):
        if self.is_authenticated:
            CartItem.objects.filter(
                user=self.user
            ).delete()

            self.cart.clear()
        else:
            self.cart.clear()
            self.session.pop(
                settings.CART_SESSION_ID, None
            )
            self.session.modified = True
