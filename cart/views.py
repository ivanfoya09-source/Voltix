from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from store.models import Product
from .cart import Cart


def cart_detail(request):
    cart = Cart(request)

    return render(request, "cart/detail.html", {
        "cart": cart,
    })


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
        available=True
    )

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        messages.error(request, "Кількість має бути більшою за нуль.")
        return redirect("cart:cart_detail")

    if product.stock <= 0:
        messages.error(request, "Цього товару немає в наявності.")
        return redirect("cart:cart_detail")

    current_quantity = cart.cart.get(
        str(product.id), {}
    ).get("quantity", 0)

    if not isinstance(current_quantity, int):
        current_quantity = 0

    if current_quantity + quantity > product.stock:
        messages.error(
            request,
            f"На складі доступно лише {product.stock} шт."
        )
        return redirect("cart:cart_detail")

    cart.add(product, quantity=quantity)

    messages.success(
        request,
        f"Товар «{product.name}» додано до кошика!"
    )

    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id,
        available=True
    )

    if str(product.id) not in cart.cart:
        messages.error(request, "Цього товару немає в кошику.")
        return redirect("cart:cart_detail")

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (ValueError, TypeError):
        messages.error(request, "Введіть правильну кількість.")
        return redirect("cart:cart_detail")

    if quantity < 1:
        cart.remove(product)
        messages.info(request, "Товар видалено з кошика.")

    elif quantity > product.stock:
        messages.error(
            request,
            f"На складі доступно лише {product.stock} шт."
        )

    else:
        cart.add(
            product,
            quantity=quantity,
            override_quantity=True
        )

        messages.success(
            request,
            "Кількість товару оновлено."
        )

    return redirect("cart:cart_detail")


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)

    product = get_object_or_404(
        Product,
        id=product_id
    )

    cart.remove(product)

    messages.success(
        request,
        "Товар видалено з кошика."
    )

    return redirect("cart:cart_detail")




# VOLTIX — AJAX CART
def ajax_cart_response(cart, product=None):

    response = {
        "success": True,
        "cart_count": len(cart),
        "cart_total": str(cart.get_total_price()),
    }

    if product is not None:
        product_id = str(product.pk)

        quantity = cart.cart.get(
            product_id, {}
        ).get("quantity", 0)

        response["product_id"] = product.pk
        response["quantity"] = quantity

        response["item_total"] = str(
            product.price * quantity
        )

    return JsonResponse(response)


@require_POST
def ajax_cart_update(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(
        Product,
        pk=product_id
    )

    product_key = str(product.pk)

    # Перевіряємо, що товар уже є у кошику.
    if product_key not in cart.cart:
        return JsonResponse(
            {
                "success": False,
                "error": "Товар відсутній у кошику."
            },
            status=404
        )

    try:
        quantity = int(request.POST.get("quantity", ""))

    except (TypeError, ValueError):
        return JsonResponse(
            {
                "success": False,
                "error": "Некоректна кількість товару."
            },
            status=400
        )

    if quantity < 1:
        return JsonResponse(
            {
                "success": False,
                "error": "Мінімальна кількість — 1."
            },
            status=400
        )

    if not product.available:
        return JsonResponse(
            {
                "success": False,
                "error": "Товар наразі недоступний."
            },
            status=400
        )

    if quantity > product.stock:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    f"На складі доступно лише "
                    f"{product.stock} шт."
                )
            },
            status=400
        )

    # Записуємо нову кількість.
    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=True,
    )

    return ajax_cart_response(cart, product)


@require_POST
def ajax_cart_remove(request, product_id):

    cart = Cart(request)

    product = get_object_or_404(
        Product,
        pk=product_id
    )

    cart.remove(product)

    return ajax_cart_response(cart, product)


# VOLTIX AJAX ADD TO CART
@require_POST
def ajax_cart_add(request, product_id):

    product = get_object_or_404(
        Product,
        pk=product_id
    )

    cart = Cart(request)

    # Перевіряємо кількість.
    try:
        quantity = int(
            request.POST.get("quantity", "1")
        )
    except (TypeError, ValueError):
        return JsonResponse(
            {
                "success": False,
                "error": "Некоректна кількість товару."
            },
            status=400
        )

    if quantity < 1:
        return JsonResponse(
            {
                "success": False,
                "error": "Кількість повинна бути більшою за нуль."
            },
            status=400
        )

    if not product.available or product.stock <= 0:
        return JsonResponse(
            {
                "success": False,
                "error": "Товар зараз недоступний."
            },
            status=400
        )

    existing_quantity = cart.cart.get(
        str(product.pk), {}
    ).get("quantity", 0)

    if existing_quantity + quantity > product.stock:
        return JsonResponse(
            {
                "success": False,
                "error": (
                    f"На складі доступно {product.stock} шт. "
                    f"У кошику вже {existing_quantity} шт."
                )
            },
            status=400
        )

    cart.add(
        product=product,
        quantity=quantity,
        override_quantity=False,
    )

    return JsonResponse(
        {
            "success": True,
            "message": (
                f"«{product.name}» додано до кошика!"
            ),
            "product_id": product.pk,
            "product_quantity": cart.cart[
                str(product.pk)
            ]["quantity"],
            "cart_count": len(cart),
            "cart_total": str(
                cart.get_total_price()
            ),
        }
    )
