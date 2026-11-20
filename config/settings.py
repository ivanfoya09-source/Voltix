
"""
VOLTIX — Django settings.

Local development:
    SQLite, local media, optional Redis.

Production:
    PostgreSQL via DATABASE_URL,
    HTTPS, secure cookies, WhiteNoise.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    value = os.getenv(name, str(default))
    return value.strip().lower() in (
        "1", "true", "yes", "on"
    )


def env_list(name, default=""):
    return [
        item.strip()
        for item in os.getenv(name, default).split(",")
        if item.strip()
    ]



DEBUG = env_bool("DEBUG", True)

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", ""
).strip()

if not SECRET_KEY:
    raise ImproperlyConfigured(
        "Set DJANGO_SECRET_KEY in .env "
        "or environment variables."
    )


ALLOWED_HOSTS = env_list(
    "ALLOWED_HOSTS",
    "127.0.0.1,localhost" if DEBUG else "",
)

if not DEBUG and not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "Set ALLOWED_HOSTS when DEBUG=False."
    )


CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS"
)



INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "store.apps.StoreConfig",
    "accounts.apps.AccountsConfig",
    "cart.apps.CartConfig",
    "orders",
    "reviews.apps.ReviewsConfig",
    "wishlist.apps.WishlistConfig",
]


ENABLE_DEBUG_TOOLBAR = (
    DEBUG and env_bool("ENABLE_DEBUG_TOOLBAR")
)

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")



MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


if ENABLE_DEBUG_TOOLBAR:
    MIDDLEWARE.insert(
        0,
        "debug_toolbar.middleware.DebugToolbarMiddleware"
    )



ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # VOLTIX
                "cart.context_processors.cart_context",
                "store.context_processors.recently_viewed",
                "wishlist.context_processors.wishlist_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"



DATABASE_URL = os.getenv(
    "DATABASE_URL", ""
).strip()

if DATABASE_URL:
    try:
        import dj_database_url
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Install dj-database-url to use DATABASE_URL."
        ) from exc

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

else:

    if not DEBUG:
        raise ImproperlyConfigured(
            "DATABASE_URL is required when DEBUG=False. "
            "Configure PostgreSQL for production."
        )

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "accounts:profile"

LOGOUT_REDIRECT_URL = "store:home"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]



LANGUAGE_CODE = "uk"

TIME_ZONE = "Europe/Kyiv"

USE_I18N = True

USE_TZ = True



STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


MEDIA_URL = "/media/"


MEDIA_ROOT = Path(
    os.getenv(
        "MEDIA_ROOT",
        str(BASE_DIR / "media"),
    )
)



USE_CLOUDINARY = env_bool("USE_CLOUDINARY", False)

if USE_CLOUDINARY and not os.getenv("CLOUDINARY_URL"):
    raise ImproperlyConfigured(
        "CLOUDINARY_URL is required when USE_CLOUDINARY=True"
    )

STORAGES = {
    "default": {
        "BACKEND": (
            "cloudinary_storage.storage.MediaCloudinaryStorage"
            if USE_CLOUDINARY
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}

import sys

if "test" in sys.argv:
    STORAGES["staticfiles"] = {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    }


import sys

if "test" in sys.argv:
    STORAGES["staticfiles"] = {
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    }



MAILERS = {
    "default": {
        "BACKEND": (
            "django.core.mail.backends."
            "console.EmailBackend"
        ),
    },
}

DEFAULT_FROM_EMAIL = (
    "VOLTIX <noreply@voltix.example>"
)



REDIS_URL = os.getenv(
    "REDIS_URL", ""
).strip()

if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends."
                "redis.RedisCache"
            ),
            "LOCATION": REDIS_URL,
            "KEY_PREFIX": "voltix",
            "TIMEOUT": 300,
        },
    }

else:
    CACHES = {
        "default": {
            "BACKEND": (
                "django.core.cache.backends."
                "locmem.LocMemCache"
            ),
            "LOCATION": "voltix-local",
            "TIMEOUT": 300,
        },
    }



CART_SESSION_ID = "voltix_cart"

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

CSRF_COOKIE_SAMESITE = "Lax"



SECURE_SSL_REDIRECT = (
    env_bool("SECURE_SSL_REDIRECT", True)
    if not DEBUG else False
)


SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG


SECURE_HSTS_SECONDS = (
    int(os.getenv("SECURE_HSTS_SECONDS", "0"))
    if not DEBUG else 0
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = False

SECURE_HSTS_PRELOAD = False

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = (
    "strict-origin-when-cross-origin"
)

X_FRAME_OPTIONS = "DENY"


if (
    not DEBUG
    and env_bool("TRUST_PROXY_SSL_HEADER", False)
):
    SECURE_PROXY_SSL_HEADER = (
        "HTTP_X_FORWARDED_PROTO",
        "https",
    )



INTERNAL_IPS = [
    "127.0.0.1",
]



DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)
