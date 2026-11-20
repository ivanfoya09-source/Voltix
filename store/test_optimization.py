from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from store.cache_utils import HOME_CATEGORIES, HOME_NEW, HOME_FEATURED
from store.models import Category, Product


class StoreTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Ноутбуки", slug="laptops")
        cls.other_category = Category.objects.create(name="Телефони", slug="phones")
        cls.product = Product.objects.create(
            category=cls.category,
            name="VOLTIX Test Laptop",
            description="Тестовий ноутбук",
            price=Decimal("1500.00"),
            stock=5,
            available=True,
        )
        cls.other = Product.objects.create(
            category=cls.other_category,
            name="VOLTIX Test Phone",
            description="Тестовий телефон",
            price=Decimal("500.00"),
            stock=2,
            available=True,
        )

    def setUp(self):
        cache.clear()

    def test_product_generates_unique_slug(self):
        duplicate_name = Product.objects.create(
            category=self.category,
            name="VOLTIX Test Laptop",
            description="Другий товар",
            price=Decimal("900.00"),
            stock=1,
        )
        self.assertTrue(duplicate_name.slug)
        self.assertNotEqual(duplicate_name.slug, self.product.slug)

    def test_home_page_opens(self):
        response = self.client.get(reverse("store:home"))
        self.assertEqual(response.status_code, 200)

    def test_catalog_search(self):
        response = self.client.get(reverse("store:product_list"), {"q": "Laptop"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VOLTIX Test Laptop")
        self.assertNotContains(response, "VOLTIX Test Phone")

    def test_catalog_category_filter(self):
        response = self.client.get(
            reverse("store:product_list"), {"category": self.category.slug}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VOLTIX Test Laptop")
        self.assertNotContains(response, "VOLTIX Test Phone")

    def test_catalog_price_filter(self):
        response = self.client.get(
            reverse("store:product_list"), {"min_price": "1000", "max_price": "2000"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VOLTIX Test Laptop")
        self.assertNotContains(response, "VOLTIX Test Phone")

    def test_product_detail_opens(self):
        response = self.client.get(
            reverse("store:product_detail", args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VOLTIX Test Laptop")

    def test_signals_clear_real_home_cache_keys(self):
        cache.set(HOME_CATEGORIES, "categories", 300)
        cache.set(HOME_NEW, "new", 300)
        cache.set(HOME_FEATURED, "featured", 300)

        with self.captureOnCommitCallbacks(execute=True):
            self.product.save()

        for key in (HOME_CATEGORIES, HOME_NEW, HOME_FEATURED):
            self.assertIsNone(cache.get(key), f"Кеш не очищено: {key}")
