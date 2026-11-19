
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from store.models import Product

from .models import WishlistItem


@login_required
def wishlist_list(request):
    """
    Сторінка обраних товарів.
    """
    wishlist_items = (
        WishlistItem.objects
        .filter(
            user=request.user,
            product__available=True,
        )
        .select_related("product", "product__category")
        .prefetch_related("product__images")
        .order_by("-created_at")
    )

    return render(
        request,
        "wishlist/wishlist.html",
        {
            "wishlist_items": wishlist_items,
        },
    )


@login_required
@require_POST
def wishlist_toggle(request, product_id):
    """
    Додавання або видалення товару з обраного.
    Підтримує звичайний POST та AJAX.
    """

    product = get_object_or_404(
        Product,
        id=product_id,
        available=True,
    )

    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if created:
        is_favorite = True
        message = "Товар додано до обраного ❤️"
    else:
        wishlist_item.delete()
        is_favorite = False
        message = "Товар видалено з обраного."

    wishlist_count = WishlistItem.objects.filter(
        user=request.user,
    ).count()

    is_ajax = (
        request.headers.get("X-Requested-With")
        == "XMLHttpRequest"
    )

    if is_ajax:
        return JsonResponse({
            "success": True,
            "is_favorite": is_favorite,
            "wishlist_count": wishlist_count,
            "message": message,
            "product_id": product.id,
        })

    messages.success(request, message)

    # Повертаємо користувача на ту сторінку,
    # звідки він натиснув сердечко.
    next_url = request.POST.get("next", "")

    if next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)

    return redirect("wishlist:list")
