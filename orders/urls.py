from django.urls import path

from . import views


app_name = "orders"

urlpatterns = [
    path(
        "checkout/",
        views.checkout_address,
        name="checkout_address"
    ),

    path(
        "checkout/review/",
        views.checkout_review,
        name="checkout_review"
    ),

    path(
        "checkout/coupon/apply/",
        views.apply_coupon,
        name="apply_coupon"
    ),

    path(
        "checkout/coupon/remove/",
        views.remove_coupon,
        name="remove_coupon"
    ),

    path(
        "checkout/confirm/",
        views.checkout_confirm,
        name="checkout_confirm"
    ),

    path(
        "checkout/success/",
        views.checkout_success,
        name="checkout_success"
    ),
    path(
    "my/",
    views.order_list,
    name="order_list"
    ),

    path(
        "my/<int:order_id>/",
        views.order_detail,
        name="order_detail"
    ),


    path(
        "my/<int:order_id>/cancel/",
        views.order_cancel,
        name="order_cancel"
    ),
]
