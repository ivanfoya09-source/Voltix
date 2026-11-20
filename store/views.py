from decimal import Decimal, InvalidOperation

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.shortcuts import get_object_or_404, render

from reviews.models import Review

from .cache_utils import (
    HOME_CATEGORIES,
    HOME_NEW,
    HOME_FEATURED,
    HOME_CACHE_TIMEOUT,
)
from .models import Category, Product


# НАЛАШТУВАННЯ 
RECENTLY_VIEWED_SESSION_KEY = "voltix_recently_viewed"
RECENTLY_VIEWED_LIMIT = 10

CATALOG_PRODUCTS_PER_PAGE = 12

REVIEWS_PER_PAGE = 5



# ДОПОМІЖНА ФУНКЦІЯ КЕШУВАННЯ
def _cached_list(cache_key, queryset):

    result = cache.get(cache_key)

    if result is None:
        result = list(queryset)

        cache.set(
            cache_key,
            result,
            HOME_CACHE_TIMEOUT,
        )

    return result



# ГОЛОВНА СТОРІНКА
def home(request):

    categories = _cached_list(
        HOME_CATEGORIES,
        Category.objects
        .filter(parent__isnull=True)
        .order_by("name"),
    )

    products = _cached_list(
        HOME_NEW,
        Product.objects
        .filter(available=True)
        .select_related("category")
        .prefetch_related("images")
        .order_by("-created_at")[:8],
    )

    featured_products = _cached_list(
        HOME_FEATURED,
        Product.objects
        .filter(
            available=True,
            is_featured=True,
        )
        .select_related("category")
        .prefetch_related("images")
        .order_by("-created_at")[:8],
    )

    context = {
        "categories": categories,
        "products": products,
        "featured_products": featured_products,
    }

    return render(
        request,
        "store/home.html",
        context,
    )


# КАТАЛОГ ТОВАРІВ
def product_list(request):

    products = (
        Product.objects
        .filter(available=True)
        .select_related("category")
        .prefetch_related("images")
    )

    categories = (
        Category.objects
        .filter(parent__isnull=True)
        .prefetch_related("children")
    )

    query = request.GET.get("q", "").strip()

    category_slug = request.GET.get(
        "category", ""
    )

    min_price = request.GET.get(
        "min_price", ""
    )

    max_price = request.GET.get(
        "max_price", ""
    )

    sort = request.GET.get(
        "sort", "newest"
    )

    # ПОШУК
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

   
    # ФІЛЬТР ЗА КАТЕГОРІЄЮ
    if category_slug:

        category = get_object_or_404(
            Category,
            slug=category_slug,
        )

        child_ids = list(
            category.get_children()
            .values_list("id", flat=True)
        )

        products = products.filter(
            category_id__in=[
                category.id,
                *child_ids,
            ]
        )


    # МІНІМАЛЬНА ЦІНА
    if min_price:

        try:
            value = Decimal(min_price)

            if value >= 0 and value.is_finite():
                products = products.filter(
                    price__gte=value
                )

        except InvalidOperation:
            pass


    # МАКСИМАЛЬНА ЦІНА
    if max_price:

        try:
            value = Decimal(max_price)

            if value >= 0 and value.is_finite():
                products = products.filter(
                    price__lte=value
                )

        except InvalidOperation:
            pass


    # СОРТУВАННЯ
    sort_options = {
        "newest": "-created_at",
        "oldest": "created_at",
        "price_asc": "price",
        "price_desc": "-price",
        "name": "name",
    }

    if sort not in sort_options:
        sort = "newest"

    products = products.order_by(
        sort_options[sort],
        "pk",
    )


    paginator = Paginator(products,CATALOG_PRODUCTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    query_params = request.GET.copy()
    query_params.pop("page", None)
    page_query = query_params.urlencode()


    context = {
        "products": page_obj,
        "categories": categories,
        "selected_category": category_slug,
        "query": query,
        "min_price": min_price,
        "max_price": max_price,
        "sort": sort,
        "page_obj": page_obj,
        "paginator": paginator,
        "page_query": page_query,
        "total_products": paginator.count,
        "products_per_page": CATALOG_PRODUCTS_PER_PAGE,
    }

    return render(
        request,
        "store/product_list.html",
        context,
    )


# СТОРІНКА ТОВАРУ
def product_detail(request, slug):

    product = get_object_or_404(
        Product.objects
        .select_related("category")
        .prefetch_related("images"),
        slug=slug,
        available=True,
    )

    recent_ids = request.session.get(
        RECENTLY_VIEWED_SESSION_KEY,
        [],
    )

    recent_ids = [
        item_id
        for item_id in recent_ids
        if item_id != product.id
    ]

    recent_ids.insert(
        0,
        product.id,
    )

    request.session[
        RECENTLY_VIEWED_SESSION_KEY
    ] = recent_ids[:RECENTLY_VIEWED_LIMIT]

    reviews_queryset = (
        Review.objects
        .filter(
            product=product,
            is_approved=True,
        )
        .select_related("user")
        .order_by(
            "-created_at",
            "-pk",
        )
    )

    review_stats = reviews_queryset.aggregate(
        average_rating=Avg("rating"),
        review_count=Count("id"),
    )

    reviews_paginator = Paginator(
        reviews_queryset,
        REVIEWS_PER_PAGE,
    )

    reviews_page_number = request.GET.get(
        "reviews_page"
    )

    reviews_page = reviews_paginator.get_page(
        reviews_page_number
    )

    can_review = False

    if request.user.is_authenticated:

        can_review = Review.has_purchased_product(
            request.user,
            product,
        )

    context = {
        "product": product,
        "approved_reviews": reviews_page,
        "reviews_page": reviews_page,
        "average_rating": review_stats[
            "average_rating"
        ],
        "review_count": review_stats[
            "review_count"
        ],
        "can_review": can_review,
    }

    return render(
        request,
        "store/product_detail.html",
        context,
    )
