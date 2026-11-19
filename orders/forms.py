from django import forms
from django.core.validators import RegexValidator


class CheckoutAddressForm(forms.Form):

    full_name = forms.CharField(
        label="Ім'я та прізвище отримувача",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Іван Петренко",
            "autocomplete": "name",
        })
    )

    email = forms.EmailField(
        label="Електронна пошта",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "example@gmail.com",
            "autocomplete": "email",
        })
    )

    phone = forms.CharField(
        label="Номер телефону",
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\+?[0-9\s()\-]{9,20}$",
                message="Введіть коректний номер телефону."
            )
        ],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+380XXXXXXXXX",
            "autocomplete": "tel",
        })
    )

    city = forms.CharField(
        label="Місто",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Київ",
            "autocomplete": "address-level2",
        })
    )

    address = forms.CharField(
        label="Адреса доставки",
        max_length=255,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Вулиця, будинок, квартира",
            "autocomplete": "street-address",
        })
    )

    postal_code = forms.CharField(
        label="Поштовий індекс",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "01001",
            "autocomplete": "postal-code",
        })
    )

class CouponApplyForm(forms.Form):
    code = forms.CharField(
        label="Промокод",
        max_length=50,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введіть промокод",
            "autocomplete": "off",
        })
    )

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()
