
from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review

        fields = [
            "rating",
            "title",
            "comment",
            "advantages",
            "disadvantages",
        ]

        widgets = {
            "rating": forms.RadioSelect(
                choices=[
                    (5, "5 зірок — Відмінно"),
                    (4, "4 зірки — Добре"),
                    (3, "3 зірки — Нормально"),
                    (2, "2 зірки — Погано"),
                    (1, "1 зірка — Дуже погано"),
                ],
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Короткий заголовок",
                    "maxlength": 150,
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Поділіться враженнями",
                }
            ),
            "advantages": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Що сподобалося?",
                }
            ),
            "disadvantages": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Що можна покращити?",
                }
            ),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError(
                "Введіть заголовок відгуку."
            )

        return title

    def clean_comment(self):
        comment = self.cleaned_data["comment"].strip()

        if not comment:
            raise forms.ValidationError(
                "Напишіть текст відгуку."
            )

        return comment
