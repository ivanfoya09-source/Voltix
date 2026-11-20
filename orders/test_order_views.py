from decimal import Decimal
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from orders.models import Order, OrderItem
from store.models import Category, Product


class OrderViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(username="test_owner", password="TestPass_12345")
        cls.stranger = User.objects.create_user(username="test_stranger", password="TestPass_12345")
        category = Category.objects.create(name="Тести замовлень", slug="test-orders")
        cls.product = Product.objects.create(
            category=category,
            name="VOLTIX Test Device",
            description="Тест",
            price=Decimal("300.00"),
            stock=10,
        )
        cls.order = Order.objects.create(
            user=cls.owner,
            full_name="Test Customer",
            email="test@example.com",
            phone="+380501234567",
            city="Київ",
            address="Тестова адреса 1",
            subtotal=Decimal("600.00"),
            total=Decimal("600.00"),
        )
        OrderItem.objects.create(
            order=cls.order,
            product=cls.product,
            product_name=cls.product.name,
            price=cls.product.price,
            quantity=2,
        )

    def test_order_item_total(self):
        item = self.order.items.first()
        self.assertEqual(item.get_total_price, Decimal("600.00"))

    def test_recent_pending_order_can_be_cancelled(self):
        self.assertTrue(self.order.can_cancel)

    def test_delivered_order_cannot_be_cancelled(self):
        self.order.status = Order.Status.DELIVERED
        self.assertFalse(self.order.can_cancel)

    def test_old_order_cannot_be_cancelled(self):
        Order.objects.filter(pk=self.order.pk).update(
            created_at=timezone.now() - timedelta(hours=25)
        )
        self.order.refresh_from_db()
        self.assertFalse(self.order.can_cancel)

    def test_order_list_requires_login(self):
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 302)

    def test_owner_sees_their_order(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("orders:order_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{self.order.pk}")

    def test_another_user_cannot_view_order_details(self):
        self.client.force_login(self.stranger)
        response = self.client.get(reverse("orders:order_detail", args=[self.order.pk]))
        self.assertEqual(response.status_code, 404)

    def test_another_user_cannot_cancel_order(self):
        self.client.force_login(self.stranger)
        response = self.client.post(reverse("orders:order_cancel", args=[self.order.pk]))
        self.assertEqual(response.status_code, 404)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING)

    def test_empty_cart_redirects_from_checkout(self):
        response = self.client.get(reverse("orders:checkout_address"))
        self.assertRedirects(response, reverse("cart:cart_detail"))

    def test_checkout_confirm_rejects_missing_session(self):
        response = self.client.post(
            reverse("orders:checkout_confirm")
        )

        self.assertRedirects(
            response,
            reverse("orders:checkout_address"),
            fetch_redirect_response=False,
        )
