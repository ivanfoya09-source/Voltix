from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path(
        "",
        views.cart_detail,
        name="cart_detail"
    ),
    path(
        "add/<int:product_id>/",
        views.cart_add,
        name="cart_add"
    ),
    path(
        "update/<int:product_id>/",
        views.cart_update,
        name="cart_update"
    ),
    path(
        "remove/<int:product_id>/",
        views.cart_remove,
        name="cart_remove"
    ),

    # AJAX оновлення кількості
    path(
        "ajax/update/<int:product_id>/",
        views.ajax_cart_update,
        name="ajax_cart_update"
    ),

    # AJAX видалення товару
    path(
        "ajax/remove/<int:product_id>/",
        views.ajax_cart_remove,
        name="ajax_cart_remove"
    ),


    path(
        "ajax/add/<int:product_id>/",
        views.ajax_cart_add,
        name="ajax_cart_add"
    ),
]
