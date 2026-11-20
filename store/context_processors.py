from .models import Product


def recently_viewed(request):
    product_ids = request.session.get(
        "voltix_recently_viewed", []
    )

    if not product_ids:
        return {
            "recently_viewed_products": []
        }

    products = (
        Product.objects
        .filter(
            id__in=product_ids,
            available=True
        )
        .select_related("category")
        .prefetch_related("images")
    )

    products_by_id = {
        product.id: product
        for product in products
    }

    ordered_products = [
        products_by_id[product_id]
        for product_id in product_ids
        if product_id in products_by_id
    ]

    return {
        "recently_viewed_products": ordered_products
    }
