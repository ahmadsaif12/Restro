from __future__ import annotations

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent


def env(key: str, default: str | None = None) -> str:
    value = os.environ.get(key, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value


ENVIRONMENT = env("ENVIRONMENT", "dev")

SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-secret-key")
DEBUG = env("DJANGO_DEBUG", "1") in {"1", "true", "True", "yes", "YES"}

ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]

DJANGO_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_celery_beat",
    "django_filters",
]

#local apps
LOCAL_APPS = [
    "apps.autho.apps.AuthoConfig",
    "apps.menu",
    "apps.events",
    "apps.inventory",
    "apps.misc",
    "apps.orders",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

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

ROOT_URLCONF = "handle_my_restore.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "handle_my_restore.wsgi.application"
ASGI_APPLICATION = "handle_my_restore.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME", "handle_my_restore"),
        "USER": env("DB_USER", "postgres"),
        "PASSWORD": env("DB_PASSWORD", "postgres"),
        "HOST": env("DB_HOST", "db"),
        "PORT": env("DB_PORT", "5432"),
        "CONN_MAX_AGE": int(env("DB_CONN_MAX_AGE", "60")),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True

#statics
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

for directory in STATICFILES_DIRS:
    os.makedirs(directory, exist_ok=True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "autho.User"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
}
#swagger settings
SPECTACULAR_SETTINGS = {
    "TITLE": "Handle My Restro API",
    "DESCRIPTION": "API documentation",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA":  False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"bearerAuth": []}],
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    "ENUM_NAME_OVERRIDES": {
        "InventoryUnitEnum": [
            "kg", "g", "l", "ml", "pcs", "dozen", "box"
        ],
    },
    "ENUM_GENERATE_CHOICE_DESCRIPTION": False,
}
#jwt
SIMPLE_JWT = {
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

EMAIL_BACKEND = env("DJANGO_EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
DEFAULT_FROM_EMAIL = env("DJANGO_DEFAULT_FROM_EMAIL", "no-reply@example.com")

REDIS_URL = env("REDIS_URL", "redis://redis:6379/0")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    }
}

#celery configurations
CELERY_BROKER_URL = env("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND", REDIS_URL)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

#django unfold for admin config
UNFOLD = {
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Overview",
                "separator": True,
                "items": [
                    {"title": "Dashboard", "icon": "dashboard", "link": "/admin/"},
                    {"title": "Executive Dashboard", "icon": "bar_chart", "link": "/admin/executive-dashboard/"},
                ],
            },
            {
                "title": "Operations",
                "separator": True,
                "items": [
                    {"title": "POS", "icon": "point_of_sale", "link": "/admin/pos/"},
                    {"title": "Preboard", "icon": "table_restaurant", "link": "/admin/preboard/"},
                    {"title": "Menu", "icon": "menu_book", "link": "/admin/menu/"},
                    {"title": "Inventory", "icon": "inventory_2", "link": "/admin/inventory/"},
                    {"title": "Orders", "icon": "receipt_long", "link": "/admin/orders/"},
                    {"title": "Kitchen Recipes", "icon": "soup_kitchen", "link": "/admin/kitchen-recipes/"},
                ],
            },
            {
                "title": "Finance",
                "separator": True,
                "items": [
                    {"title": "Expense", "icon": "payments", "link": "/admin/expense/"},
                    {"title": "Calendar", "icon": "calendar_month", "link": "/admin/calendar/"},
                    {"title": "Credits", "icon": "credit_score", "link": "/admin/credits/"},
                    {"title": "Reports", "icon": "analytics", "link": "/admin/reports/"},
                ],
            },
            {
                "title": "Management",
                "separator": True,
                "items": [
                    {"title": "Credit Management", "icon": "account_balance_wallet", "link": "/admin/credit-management/"},
                    {"title": "Staff Management", "icon": "badge", "link": "/admin/staff/"},
                    {"title": "Vendor Management", "icon": "local_shipping", "link": "/admin/vendors/"},
                    {"title": "QR Menu", "icon": "qr_code_2", "link": "/admin/qr-menu/"},
                ],
            },
        ],
    }
}

#esewa settings

ESEWA_SETTINGS = {
    "MERCHANT_ID": "EPAYTEST",
    "SECRET_KEY": "8gBm/:&EnhH.1/q",
    "INITIATE_URL": "https://rc-epay.esewa.com.np/api/epay/main/v2/form",
    "SUCCESS_URL": "http://localhost:8000/api/orders/esewa_success/",
    "FAILURE_URL": "http://localhost:8000/api/orders/esewa_failure/",
}