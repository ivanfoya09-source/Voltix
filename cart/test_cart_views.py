"""VOLTIX: tests for guest cart and AJAX validation."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product


class CartViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name="Периферія", slug="peripherals")
        cls.product = Product.objects.create(
            category=category,
            name="VOLTIX Test Mouse",
            description="Тестова миша",
            price=Decimal("199.00"),
            stock=3,
            available=True,
        )

    def add_url(self):
        return reverse("cart:ajax_cart_add", args=[self.product.pk])

    def test_cart_page_opens(self):
        response = self.client.get(reverse("cart:cart_detail"))
        self.assertEqual(response.status_code, 200)

    def test_ajax_add_requires_post(self):
        response = self.client.get(self.add_url())
        self.assertEqual(response.status_code, 405)

    def test_ajax_add_valid_quantity(self):
        response = self.client.post(self.add_url(), {"quantity": "2"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["product_quantity"], 2)
        self.assertEqual(data["cart_count"], 2)

    def test_ajax_add_rejects_zero(self):
        response = self.client.post(self.add_url(), {"quantity": "0"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_ajax_add_rejects_non_numeric_value(self):
        response = self.client.post(self.add_url(), {"quantity": "invalid"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_ajax_add_rejects_more_than_stock(self):
        response = self.client.post(self.add_url(), {"quantity": "4"})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    def test_ajax_update_then_remove(self):
        self.client.post(self.add_url(), {"quantity": "1"})
        update_url = reverse("cart:ajax_cart_update", args=[self.product.pk])
        updated = self.client.post(update_url, {"quantity": "3"})
        self.assertEqual(updated.status_code, 200)
        self.assertEqual(updated.json()["quantity"], 3)

        remove_url = reverse("cart:ajax_cart_remove", args=[self.product.pk])
        removed = self.client.post(remove_url)
        self.assertEqual(removed.status_code, 200)
        self.assertEqual(removed.json()["cart_count"], 0)
