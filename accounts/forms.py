from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser, UserProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email"
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser

        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
        )

        labels = {
            "username": "Логін",
            "first_name": "Ім'я",
            "last_name": "Прізвище",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if CustomUser.objects.filter(
            email__iexact=email
        ).exists():
            raise forms.ValidationError(
                "Ця електронна адреса вже використовується."
            )

        return email


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser

        fields = (
            "first_name",
            "last_name",
            "email",
        )

        labels = {
            "first_name": "Ім'я",
            "last_name": "Прізвище",
            "email": "Email",
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if CustomUser.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "Ця електронна адреса вже використовується."
            )

        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile

        fields = (
            "phone",
            "city",
            "address",
        )

        labels = {
            "phone": "Номер телефону",
            "city": "Місто",
            "address": "Адреса",
        }
