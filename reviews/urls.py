from django.urls import path

from . import views


app_name = "reviews"

urlpatterns = [
    path(
        "product/<slug:product_slug>/write/",
        views.review_create_or_edit,
        name="write",
    ),
]
