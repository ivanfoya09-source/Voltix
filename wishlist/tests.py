
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product
from .models import WishlistItem


User = get_user_model()


class WishlistTests(TestCase):

    def setUp(self):
        # Тестовий користувач
        self.user = User.objects.create_user(
            username="wishlist_tester",
            email="wishlist@example.com",
            password="TestPassword123!",
        )

        # Категорія
        self.category = Category.objects.create(
            name="Тестова електроніка",
            slug="test-electronics",
        )

        # Товар
        self.product = Product.objects.create(
            category=self.category,
            name="Тестовий товар VOLTIX",
            description="Перевірка обраних товарів",
            price=Decimal("1999.00"),
            stock=10,
            available=True,
        )

        self.toggle_url = reverse(
            "wishlist:toggle",
            args=[self.product.id],
        )

        self.list_url = reverse("wishlist:list")

    # 1. Гість не може додавати товари
    def test_guest_cannot_add_to_wishlist(self):
        response = self.client.post(self.toggle_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(WishlistItem.objects.count(), 0)

    # 2. Авторизований користувач додає товар
    def test_user_can_add_product(self):
        self.client.force_login(self.user)

        response = self.client.post(self.toggle_url)

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            WishlistItem.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )

    # 3. Повторне натискання видаляє товар
    def test_toggle_removes_existing_product(self):
        self.client.force_login(self.user)

        self.client.post(self.toggle_url)
        self.client.post(self.toggle_url)

        self.assertFalse(
            WishlistItem.objects.filter(
                user=self.user,
                product=self.product,
            ).exists()
        )

    # 4. AJAX повертає правильний JSON
    def test_ajax_add_product(self):
        self.client.force_login(self.user)

        response = self.client.post(
            self.toggle_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertTrue(data["success"])
        self.assertTrue(data["is_favorite"])
        self.assertEqual(data["wishlist_count"], 1)
        self.assertEqual(
            data["product_id"],
            self.product.id,
        )

    # 5. AJAX видаляє товар і змінює лічильник
    def test_ajax_remove_product(self):
        self.client.force_login(self.user)

        WishlistItem.objects.create(
            user=self.user,
            product=self.product,
        )

        response = self.client.post(
            self.toggle_url,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        data = response.json()

        self.assertFalse(data["is_favorite"])
        self.assertEqual(data["wishlist_count"], 0)
        self.assertFalse(WishlistItem.objects.exists())

    # 6. GET не повинен змінювати Wishlist
    def test_get_cannot_toggle_wishlist(self):
        self.client.force_login(self.user)

        response = self.client.get(self.toggle_url)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(WishlistItem.objects.count(), 0)

    # 7. На сторінці обраного видно збережений товар
    def test_wishlist_page_displays_product(self):
        self.client.force_login(self.user)

        WishlistItem.objects.create(
            user=self.user,
            product=self.product,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.product.name,
        )

    # 8. Неактивний товар не можна додати
    def test_unavailable_product_cannot_be_added(self):
        self.client.force_login(self.user)

        self.product.available = False
        self.product.save()

        response = self.client.post(self.toggle_url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(WishlistItem.objects.count(), 0)

    # 9. Кожен користувач має власне обране
    def test_users_have_separate_wishlists(self):
        another_user = User.objects.create_user(
            username="second_wishlist_user",
            password="TestPassword123!",
        )

        WishlistItem.objects.create(
            user=self.user,
            product=self.product,
        )

        self.client.force_login(another_user)

        response = self.client.get(self.list_url)

        self.assertNotContains(
            response,
            self.product.name,
        )

    # 10. Неавторизований користувач
    # перенаправляється зі сторінки обраного
    def test_guest_cannot_open_wishlist(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 302)
