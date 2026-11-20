import uuid
from datetime import date


from .status_services import OrderStatusError, cancel_order

from django.contrib import messages
from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .emails import send_order_confirmation

from cart.cart import Cart
from store.models import Product

from .forms import CheckoutAddressForm, CouponApplyForm
from .models import Coupon, Order, OrderItem, OrderStatusHistory
from .services import (
    COUPON_SESSION_KEY,
    calculate_totals,
    get_valid_coupon,
)


CHECKOUT_SESSION_KEY = "voltix_checkout"
CHECKOUT_TOKEN_KEY = "voltix_checkout_token"
LAST_ORDER_KEY = "voltix_last_order_id"


class CheckoutError(Exception):
    pass


def get_checkout_items(cart):
    items = list(cart)

    if not items or len(items) != len(cart.cart):
        raise CheckoutError(
            "Склад кошика змінився. Перевірте товари."
        )

    for item in items:
        product = item["product"]
        quantity = item["quantity"]

        if (
            not product.available
            or quantity < 1
            or product.stock < quantity
        ):
            raise CheckoutError(
                f"Недостатньо товару: {product.name}"
            )

    return items



#  АДРЕСА
def checkout_address(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(
            request,
            "Спочатку додайте товари до кошика."
        )
        return redirect("cart:cart_detail")

    if request.method == "POST":
        form = CheckoutAddressForm(request.POST)

        if form.is_valid():
            request.session[CHECKOUT_SESSION_KEY] = (
                form.cleaned_data
            )

            if not request.session.get(CHECKOUT_TOKEN_KEY):
                request.session[CHECKOUT_TOKEN_KEY] = str(
                    uuid.uuid4()
                )

            return redirect("orders:checkout_review")

    else:
        saved_data = request.session.get(
            CHECKOUT_SESSION_KEY
        )

        if saved_data:
            initial = saved_data.copy()

        elif request.user.is_authenticated:
            profile = getattr(
                request.user,
                "profile",
                None
            )

            initial = {
                "full_name": request.user.get_full_name(),
                "email": request.user.email,
                "phone": (
                    profile.phone if profile else ""
                ),
                "city": (
                    profile.city if profile else ""
                ),
                "address": (
                    profile.address if profile else ""
                ),
            }

        else:
            initial = {}

        form = CheckoutAddressForm(initial=initial)

    return render(
        request,
        "orders/checkout_address.html",
        {
            "form": form,
            "cart": cart,
            "checkout_step": 1,
        }
    )



# ПЕРЕВІРКА
def checkout_review(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(
            request,
            "Ваш кошик порожній."
        )
        return redirect("cart:cart_detail")

    checkout_data = request.session.get(
        CHECKOUT_SESSION_KEY
    )

    if not checkout_data:
        messages.info(
            request,
            "Спочатку заповніть дані доставки."
        )
        return redirect("orders:checkout_address")

    try:
        cart_items = get_checkout_items(cart)

    except CheckoutError as error:
        messages.error(request, str(error))
        return redirect("cart:cart_detail")

    coupon_id = request.session.get(
        COUPON_SESSION_KEY
    )

    coupon = get_valid_coupon(coupon_id)

    if coupon_id and coupon is None:
        request.session.pop(
            COUPON_SESSION_KEY, None
        )
        request.session.modified = True

        messages.warning(
            request,
            "Промокод більше не діє."
        )

    totals = calculate_totals(cart, coupon)

    return render(
        request,
        "orders/checkout_review.html",
        {
            "cart": cart,
            "cart_items": cart_items,
            "checkout_data": checkout_data,
            "coupon": coupon,
            "coupon_form": CouponApplyForm(),
            "totals": totals,
            "checkout_step": 2,
        }
    )



# ЗАСТОСУВАННЯ ПРОМОКОДУ
@require_POST
def apply_coupon(request):
    if not request.session.get(CHECKOUT_SESSION_KEY):
        return redirect("orders:checkout_address")

    if len(Cart(request)) == 0:
        return redirect("cart:cart_detail")

    form = CouponApplyForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Введіть правильний промокод."
        )
        return redirect("orders:checkout_review")

    code = form.cleaned_data["code"]

    coupon = Coupon.objects.filter(
        code__iexact=code
    ).first()

    if coupon and coupon.is_valid:
        request.session[COUPON_SESSION_KEY] = coupon.pk

        messages.success(
            request,
            f"Промокод {coupon.code} застосовано!"
        )
    else:
        request.session.pop(
            COUPON_SESSION_KEY, None
        )
        request.session.modified = True

        messages.error(
            request,
            "Промокод недійсний або термін його дії минув."
        )

    return redirect("orders:checkout_review")


@require_POST
def remove_coupon(request):
    request.session.pop(
        COUPON_SESSION_KEY, None
    )
    request.session.modified = True

    messages.info(
        request,
        "Промокод прибрано."
    )

    return redirect("orders:checkout_review")


# СТВОРЕННЯ ЗАМОВЛЕННЯ
@require_POST
def checkout_confirm(request):
    checkout_data = request.session.get(
        CHECKOUT_SESSION_KEY
    )

    token_value = request.session.get(
        CHECKOUT_TOKEN_KEY
    )

    if not checkout_data or not token_value:
        messages.error(
            request,
            "Спочатку заповніть дані оформлення."
        )
        return redirect("orders:checkout_address")

    try:
        checkout_token = uuid.UUID(token_value)
    except (ValueError, TypeError):
        messages.error(
            request,
            "Некоректний ідентифікатор оформлення."
        )
        return redirect("orders:checkout_address")

    existing_order = Order.objects.filter(
        checkout_token=checkout_token
    ).first()

    if existing_order:
        request.session[LAST_ORDER_KEY] = existing_order.pk
        return redirect("orders:checkout_success")

    cart = Cart(request)

    try:
        get_checkout_items(cart)

        # Повторно перевіряємо форму доставки.
        address_form = CheckoutAddressForm(
            checkout_data
        )

        if not address_form.is_valid():
            raise CheckoutError(
                "Дані доставки потребують виправлення."
            )

        data = address_form.cleaned_data

        with transaction.atomic():
            cart_items = get_checkout_items(cart)

            coupon_id = request.session.get(
                COUPON_SESSION_KEY
            )

            coupon = None

            if coupon_id:
                coupon = get_valid_coupon(coupon_id)

                if coupon is None:
                    raise CheckoutError(
                        "Промокод більше не діє."
                    )

                updated_coupon = Coupon.objects.filter(
                    pk=coupon.pk,
                    is_active=True,
                    valid_from__lte=timezone.now(),
                    valid_until__gte=timezone.now(),
                    used_count__lt=F("max_uses"),
                ).update(
                    used_count=F("used_count") + 1
                )

                if updated_coupon != 1:
                    raise CheckoutError(
                        "Ліміт використань промокоду вичерпано."
                    )

            totals = calculate_totals(
                cart,
                coupon
            )

            for item in cart_items:
                product = item["product"]
                quantity = item["quantity"]

                updated = Product.objects.filter(
                    pk=product.pk,
                    available=True,
                    stock__gte=quantity,
                ).update(
                    stock=F("stock") - quantity
                )

                if updated != 1:
                    raise CheckoutError(
                        f"Недостатньо товару: {product.name}"
                    )

            order = Order.objects.create(
                checkout_token=checkout_token,
                user=(
                    request.user
                    if request.user.is_authenticated
                    else None
                ),
                full_name=data["full_name"],
                email=data["email"],
                phone=data["phone"],
                city=data["city"],
                address=data["address"],
                postal_code=data["postal_code"],
                coupon=coupon,
                discount_percent=totals["discount_percent"],
                subtotal=totals["subtotal"],
                discount_amount=totals["discount_amount"],
                total=totals["total"],
                status=Order.Status.PENDING,
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    price=item["product"].price,
                    quantity=item["quantity"],
                )
                for item in cart_items
            ])

            
            OrderStatusHistory.objects.create(
                order=order,
                old_status="",
                new_status=Order.Status.PENDING,
                changed_by=None,
                note="Замовлення створено покупцем.",
            )

            transaction.on_commit(
                lambda order_id=order.pk: send_order_confirmation(order_id)
            )


    except CheckoutError as error:
        messages.error(request, str(error))
        return redirect("orders:checkout_review")

    except IntegrityError:

        existing_order = Order.objects.filter(
            checkout_token=checkout_token
        ).first()

        if existing_order:
            request.session[LAST_ORDER_KEY] = existing_order.pk
            return redirect("orders:checkout_success")

        messages.error(
            request,
            "Не вдалося створити замовлення."
        )
        return redirect("orders:checkout_review")

    cart.clear()

    request.session[LAST_ORDER_KEY] = order.pk

    for key in (
        CHECKOUT_SESSION_KEY,
        CHECKOUT_TOKEN_KEY,
        COUPON_SESSION_KEY,
    ):
        request.session.pop(key, None)

    request.session.modified = True

    messages.success(
        request,
        f"Замовлення №{order.pk} успішно створено!"
    )

    return redirect("orders:checkout_success")


# СТОРІНКА УСПІХУ
def checkout_success(request):
    order_id = request.session.get(
        LAST_ORDER_KEY
    )

    if not order_id:
        return redirect("store:home")

    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        pk=order_id,
    )

    return render(
        request,
        "orders/checkout_success.html",
        {
            "order": order,
            "checkout_step": 3,
        }
    )


# МОЇ ЗАМОВЛЕННЯ
@login_required
def order_list(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .order_by("-created_at", "-pk")
    )

    paginator = Paginator(orders, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "orders/order_list.html",
        {
            "page_obj": page_obj,
            "orders": page_obj,
        }
    )



# ДЕТАЛІ ЗАМОВЛЕННЯ
@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects
        .filter(user=request.user)
        .select_related("coupon")
        .prefetch_related(
            "items",
            "status_history"
        ),
        pk=order_id,
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
        }
    )





# СКАСУВАННЯ ПОКУПЦЕМ
@login_required
@require_POST
def order_cancel(request, order_id):

    order = get_object_or_404(
        Order,
        pk=order_id,
        user=request.user,
    )

    try:
        cancel_order(
            order_id=order.pk,
            user=request.user,
        )

    except OrderStatusError as error:
        messages.error(
            request,
            str(error)
        )

    else:
        messages.success(
            request,
            f"Замовлення №{order.pk} скасовано. "
            "Товари повернуто на склад."
        )

    return redirect(
        "orders:order_detail",
        order_id=order.pk,
    )
