from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from store.models import Product

from .forms import ReviewForm
from .models import Review



@login_required
def review_create_or_edit(request, product_slug):
    product = get_object_or_404(
        Product,
        slug=product_slug,
    )

    # Дозволяємо відгук лише після доставки товару.
    can_review = Review.has_purchased_product(
        request.user,
        product,
    )

    if not can_review:
        messages.error(
            request,
            "Відгук можна залишити лише після "
            "отримання цього товару.",
        )
        return redirect(
            "store:product_detail",
            slug=product.slug,
        )

    # Якщо відгук уже існує, редагуємо його.
    review = Review.objects.filter(
        product=product,
        user=request.user,
    ).first()

    if request.method == "POST":
        form = ReviewForm(
            request.POST,
            instance=review,
        )

        if form.is_valid():
            saved_review = form.save(commit=False)

            saved_review.product = product
            saved_review.user = request.user

            # Кожен новий або змінений відгук
            # повторно надходить на модерацію.
            saved_review.is_approved = False
            saved_review.save()

            if review:
                messages.success(
                    request,
                    "Відгук оновлено та передано "
                    "на повторну модерацію.",
                )
            else:
                messages.success(
                    request,
                    "Дякуємо за відгук! "
                    "Його передано на модерацію.",
                )

            return redirect(
                "store:product_detail",
                slug=product.slug,
            )

    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "reviews/review_form.html",
        {
            "form": form,
            "product": product,
            "review": review,
        },
    )
