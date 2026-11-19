from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit

from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile


RATE_LIMIT_MESSAGE = (
    "Забагато спроб за короткий час. Спробуйте знову через хвилину."
)


def rate_limited_response():
    response = HttpResponse(RATE_LIMIT_MESSAGE, status=429, content_type="text/plain; charset=utf-8")
    response["Retry-After"] = "60"
    return response


class VoltixLoginView(LoginView):
    template_name = "accounts/login.html"

    # Ліміт стосується тільки POST. GET сторінки входу не обмежуємо.
    @method_decorator(ratelimit(group="voltix_login", key="ip", rate="5/m", method="POST", block=False))
    def post(self, request, *args, **kwargs):
        if getattr(request, "limited", False):
            return rate_limited_response()
        return super().post(request, *args, **kwargs)


@ratelimit(group="voltix_register", key="ip", rate="3/m", method="POST", block=False)
def register_view(request):
    if getattr(request, "limited", False):
        return rate_limited_response()

    if request.user.is_authenticated:
        return redirect("accounts:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Вітаємо! Реєстрація пройшла успішно.")
            return redirect("accounts:profile")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, "Профіль успішно оновлено!")
            return redirect("accounts:profile")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(request, "accounts/profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })
