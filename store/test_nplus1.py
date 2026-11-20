from decimal import Decimal

from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from store.models import Category, Product


class StorefrontNPlusOneTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="N+1 test category", slug="n-plus-one-test-category"
        )

        for number in range(12):
            Product.objects.create(
                category=cls.category,
                name=f"N+1 sample {number}",
                description="Sample product for SQL query count test",
                price=Decimal("199.00"),
                stock=5,
                available=True,
                is_featured=True,
            )

    def _query_count(self, url):
        cache.clear()
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return len(queries)

    def test_catalog_query_count_does_not_grow_with_products(self):

        url = reverse("store:product_list")
        full_count = self._query_count(url)

        Product.objects.exclude(pk=Product.objects.first().pk).delete()
        one_count = self._query_count(url)
        self.assertLessEqual(
            full_count, one_count + 3,
            f"Catalog query count grows with products: 12={full_count}, 1={one_count}",
        )

    def test_home_query_count_does_not_grow_with_products(self):
        url = reverse("store:home")
        full_count = self._query_count(url)
        Product.objects.exclude(pk=Product.objects.first().pk).delete()
        one_count = self._query_count(url)
        self.assertLessEqual(
            full_count, one_count + 3,
            f"Home query count grows with products: 12={full_count}, 1={one_count}",
        )

    def test_product_detail_query_count_has_upper_bound(self):
        product = Product.objects.first()
        url = reverse("store:product_detail", args=[product.slug])
        count = self._query_count(url)
        self.assertLessEqual(
            count, 12,
            f"Product detail made {count} SQL queries; inspect product gallery or recently viewed",
        )
