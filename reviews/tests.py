from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from orders.models import Order, OrderItem
from store.models import Category, Product

from .models import Review


User = get_user_model()


class ReviewTests(TestCase):

    def setUp(self):
        # 1. Створюємо тестового покупця
        self.user = User.objects.create_user(
            username="review_tester",
            email="review_tester@example.com",
            password="TestPassword123!",
        )

        # 2. Створюємо категорію
        self.category = Category.objects.create(
            name="Тестові ноутбуки",
            slug="test-laptops",
        )

        # 3. Створюємо товар
        self.product = Product.objects.create(
            category=self.category,
            name="Тестовий ноутбук VOLTIX",
            description="Товар для тестування відгуків",
            price=Decimal("25000.00"),
            stock=5,
            available=True,
        )

        # 4. Створюємо доставлене замовлення
        self.order = Order.objects.create(
            user=self.user,
            full_name="Тестовий Покупець",
            email="review_tester@example.com",
            phone="+380991234567",
            city="Київ",
            address="Тестова адреса, 1",
            status=Order.Status.DELIVERED,
            subtotal=Decimal("25000.00"),
            total=Decimal("25000.00"),
        )

        # 5. Додаємо товар до замовлення
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            price=self.product.price,
            quantity=1,
        )

    def create_review(self, **kwargs):

        data = {
            "user": self.user,
            "product": self.product,
            "rating": 5,
            "title": "Чудовий товар",
            "comment": "Усе працює правильно.",
            "is_approved": False,
        }

        data.update(kwargs)

        return Review.objects.create(**data)

    # ТЕСТ 1
    def test_delivered_order_allows_review(self):
        self.assertTrue(
            Review.has_purchased_product(
                self.user,
                self.product,
            )
        )

    # ТЕСТ 2
    def test_pending_order_does_not_allow_review(self):
        self.order.status = Order.Status.PROCESSING
        self.order.save()

        self.assertFalse(
            Review.has_purchased_product(
                self.user,
                self.product,
            )
        )

    # ТЕСТ 3
    def test_user_without_purchase_cannot_review(self):
        another_user = User.objects.create_user(
            username="another_buyer",
            password="TestPassword123!",
        )

        self.assertFalse(
            Review.has_purchased_product(
                another_user,
                self.product,
            )
        )

        with self.assertRaises(ValidationError):
            self.create_review(user=another_user)

    # ТЕСТ 4
    def test_rating_must_be_between_1_and_5(self):
        with self.assertRaises(ValidationError):
            self.create_review(rating=0)

        with self.assertRaises(ValidationError):
            self.create_review(rating=6)

        self.assertEqual(
            Review.objects.count(),
            0,
        )

    # ТЕСТ 5
    def test_only_one_review_per_product_and_user(self):
        self.create_review()

        with self.assertRaises(ValidationError):
            self.create_review(title="Другий відгук")

        self.assertEqual(
            Review.objects.count(),
            1,
        )

    # ТЕСТ 6
    def test_unapproved_review_is_hidden(self):
        review = self.create_review(
            title="Прихований тестовий відгук",
        )

        url = reverse(
            "store:product_detail",
            kwargs={"slug": self.product.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            review.title,
        )

        self.assertEqual(
            response.context["review_count"],
            0,
        )

    # ТЕСТ 7
    def test_approved_review_is_visible(self):
        review = self.create_review(
            title="Схвалений тестовий відгук",
            is_approved=True,
        )

        url = reverse(
            "store:product_detail",
            kwargs={"slug": self.product.slug},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            review.title,
        )

        self.assertEqual(
            response.context["review_count"],
            1,
        )

        self.assertEqual(
            response.context["average_rating"],
            5,
        )

    # ТЕСТ 8
    def test_review_edit_requires_new_approval(self):
        review = self.create_review(
            is_approved=True,
        )

        self.client.force_login(self.user)

        url = reverse(
            "reviews:write",
            kwargs={"product_slug": self.product.slug},
        )

        response = self.client.post(
            url,
            {
                "rating": 4,
                "title": "Оновлений відгук",
                "comment": "Відредагований текст відгуку.",
                "advantages": "Гарна якість",
                "disadvantages": "Немає",
            },
        )

        self.assertEqual(response.status_code, 302)

        review.refresh_from_db()

        self.assertEqual(review.rating, 4)
        self.assertEqual(review.title, "Оновлений відгук")
        self.assertFalse(review.is_approved)

    # ТЕСТ 9
    def test_user_without_purchase_cannot_submit(self):
        self.order.status = Order.Status.CANCELLED
        self.order.save()

        self.client.force_login(self.user)

        url = reverse(
            "reviews:write",
            kwargs={"product_slug": self.product.slug},
        )

        response = self.client.post(
            url,
            {
                "rating": 5,
                "title": "Тест без покупки",
                "comment": "Цей відгук не повинен зберегтися.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.exists())
