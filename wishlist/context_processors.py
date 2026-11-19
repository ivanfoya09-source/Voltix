
from .models import WishlistItem


def wishlist_context(request):
    if not request.user.is_authenticated:
        return {
            "wishlist_count": 0,
            "wishlist_product_ids": set(),
        }

    product_ids = set(
        WishlistItem.objects.filter(
            user=request.user
        ).values_list("product_id", flat=True)
    )

    return {
        "wishlist_count": len(product_ids),
        "wishlist_product_ids": product_ids,
    }
