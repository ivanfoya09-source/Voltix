from django.conf import settings
from django.core.cache import caches
from django.test import TestCase, override_settings
from django.urls import reverse


# Локальний кеш для авто тестів
@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "voltix-ratelimit-tests",
        }
    }
)
class AccountRateLimitTests(TestCase):

    def setUp(self):
        super().setUp()

        cache_alias = getattr(
            settings,
            "RATELIMIT_USE_CACHE",
            "default"
        )

        caches[cache_alias].clear()

        # Окрема IP-адреса для тестів авторизації
        self.client.defaults["REMOTE_ADDR"] = "192.0.2.100"

    def tearDown(self):
        cache_alias = getattr(
            settings,
            "RATELIMIT_USE_CACHE",
            "default"
        )

        caches[cache_alias].clear()

        super().tearDown()

    def test_login_post_limit(self):
        url = reverse("accounts:login")

        for i in range(5):
            response = self.client.post(
                url,
                {
                    "username": "not-existing",
                    "password": "wrong"
                }
            )

            self.assertNotEqual(
                response.status_code,
                429
            )

        response = self.client.post(
            url,
            {
                "username": "not-existing",
                "password": "wrong"
            }
        )

        self.assertEqual(
            response.status_code,
            429
        )

        self.assertEqual(
            response.headers["Retry-After"],
            "60"
        )

    def test_register_post_limit(self):
        url = reverse("accounts:register")

        for i in range(3):
            response = self.client.post(
                url,
                {}
            )

            self.assertNotEqual(
                response.status_code,
                429
            )

        response = self.client.post(
            url,
            {}
        )

        self.assertEqual(
            response.status_code,
            429
        )

    def test_get_pages_are_not_limited(self):
        for _ in range(7):
            self.assertEqual(
                self.client.get(
                    reverse("accounts:login")
                ).status_code,
                200
            )

            self.assertEqual(
                self.client.get(
                    reverse("accounts:register")
                ).status_code,
                200
            )
