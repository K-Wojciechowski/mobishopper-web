"""Django settings for mobishopper."""

import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if "SECRET_KEY" in os.environ:
    SECRET_KEY = os.getenv("SECRET_KEY")
else:
    import sys

    print("Secret key missing, using random unreproducible value!", file=sys.stderr)
    from django.core.management.utils import get_random_secret_key

    SECRET_KEY = get_random_secret_key()

MOBISHOPPER_ENV = os.getenv("MOBISHOPPER_ENV", "dev")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = MOBISHOPPER_ENV in ("dev", "debug")
DEBUG_TOOLBAR = MOBISHOPPER_ENV in ("dev_debug", "debug")

ALLOWED_HOSTS = ["mobishopper.krzysztofwojciechowski.pl"]
if DEBUG:
    ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "bootstrap4",
    "bootstrap_datepicker_plus",
    "ms_baseline",
    "ms_products",
    "ms_deals",
    "ms_maps",
    "ms_userdata",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "ms_baseline.utils.StoreContextMiddleware",
]

if DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

ROOT_URLCONF = "mobishopper.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "mobishopper.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "db.sqlite3")}}

AUTH_USER_MODEL = "ms_baseline.MsUser"


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators
"""
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
"""

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "pl-pl"
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

TIME_ZONE = "Europe/Warsaw"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "/media/"


# MobiShopper settings
LOGOUT_REDIRECT_URL = "/"
LOGIN_REDIRECT_URL = "/"

MOBISHOPPER_PAGE_SIZE = 30
MOBISHOPPER_MODAL_PAGE_SIZE = 15
MOBISHOPPER_REST_PAGE_SIZE = 30

MOBISHOPPER_EMAIL = "mobishopper@krzysztofwojciechowski.pl"
MOBISHOPPER_INVITE_SUBJECT = "[MobiShopper] {user} zaprasza do listy zakupów"
MOBISHOPPER_INVITE_PLAINTEXT = (
    "{user} zaprosił(a) Cię do przeglądania i edytowania listy zakupów w aplikacji MobiShopper.\n"
    "Aby dołączyć do listy, kliknij ten link na telefonie:\n{link}\n\nZaproszenie wygaśnie {date}."
)
MOBISHOPPER_INVITE_HTML = (
    "<strong>{user}</strong> zaprosił(a) Cię do przeglądania i edytowania listy zakupów w aplikacji MobiShopper.<br>"
    'Aby dołączyć do listy, kliknij ten link na telefonie:\n<a href="{link}">{link}</a><br><br>'
    "<small>Zaproszenie wygaśnie {date}.</small>"
)

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "ms_baseline.api_utils.PageNumberIncludedPagination",
    "PAGE_SIZE": MOBISHOPPER_REST_PAGE_SIZE,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
}

MOBISHOPPER_MENU = [
    {"title": "Strona główna", "dest": "ms_baseline:management_home", "app": "ms_baseline"},
    {
        "title": "Produkty",
        "dest": "ms_products:products_overview",
        "app": "ms_products",
        "xperm": "is_management_employee",
    },
    {
        "title": "Promocje",
        "dest": "ms_deals:deals_overview",
        "app": "ms_deals",
        "perm": "can_manage_deals",
        "gperm": "can_manage_global_deals",
    },
    {"title": "Mapy i lokalizacje", "dest": "ms_maps:maps_overview", "app": "ms_maps", "perm": "can_manage_maps"},
    {
        "title": "Statystyki",
        "dest": "ms_userdata:stats_overview",
        "app": "ms_userdata",
        "perm": "can_view_statistics",
        "gperm": "can_view_global_statistics",
    },
    {
        "title": "Użytkownicy",
        "dest": "ms_baseline:users_list",
        "app": "ms_baseline_users",
        "perm": "can_manage_employees",
        "gperm": ["can_manage_users", "is_superuser"],
    },
    {
        "title": "Sklepy",
        "dest": "ms_baseline:stores_list",
        "app": "ms_baseline_stores",
        "gperm": ["can_manage_stores", "is_superuser"],
    },
]

MOBISHOPPER_SIDEBAR = {
    "ms_products": {
        "title": "Produkty",
        "groups": [
            {
                "heading": None,
                "items": [
                    {"title": "Przegląd", "dest": "ms_products:products_overview"},
                    {
                        "title": "Dodaj produkt",
                        "dest": "ms_products:add",
                        "perm": "can_manage_products",
                        "gperm": "can_manage_global_products",
                    },
                ],
            },
            {
                "heading": "Szukaj i Zarządzaj",
                "items": [
                    {"title": "Lista", "dest": "ms_products:list"},
                    {"title": "Wyszukaj", "dest": "ms_products:search"},
                    {"title": "Ostatnie i Przyszłe", "dest": "ms_products:recent_upcoming"},
                ],
            },
            {
                "heading": "Organizuj",
                "items": [
                    {"title": "Kategorie", "dest": "ms_products:categories", "gperm": "can_manage_global_products"},
                    {
                        "title": "Globalne Subalejki",
                        "dest": "ms_products:global_subaisles",
                        "gperm": "can_manage_global_products",
                    },
                    {
                        "title": "Grupy",
                        "dest": "ms_products:groups",
                        "perm": "can_manage_products",
                        "gperm": "can_manage_global_products",
                    },
                    {"title": "Właściwości", "dest": "ms_products:properties", "gperm": "can_manage_global_products"},
                    {
                        "title": "Sprzedawcy",
                        "dest": "ms_products:vendors",
                        "perm": "can_manage_products",
                        "gperm": "can_manage_global_products",
                    },
                    {"title": "Promocje", "dest": "ms_deals:deals_overview", "gperm": "can_manage_global_deals"},
                ],
                "perm": "can_manage_products",
                "gperm": "can_manage_global_products",
            },
            {
                "heading": "Produkty w sklepie",
                "items": [
                    {
                        "title": "Lokalne nadpisania",
                        "dest": "ms_products:local_overrides",
                        "perm": "can_manage_products",
                    },
                    {"title": "Promocje w sklepie", "dest": "ms_deals:deals_list_store", "perm": "can_manage_deals"},
                ],
                "perm": "can_manage_products",
                "gperm": "",
            },
        ],
    },
    "ms_deals": {
        "title": "Promocje",
        "groups": [
            {
                "heading": None,
                "items": [
                    {"title": "Przegląd", "dest": "ms_deals:deals_overview"},
                ],
            },
            {
                "heading": "Promocje",
                "items": [
                    {"title": "Lista promocji", "dest": "ms_deals:deals_list"},
                    {"title": "Dodaj promocję", "dest": "ms_deals:deals_add"},
                ],
            },
            {
                "heading": "Kupony",
                "items": [
                    {"title": "Lista kuponów", "dest": "ms_deals:coupons_list"},
                    {"title": "Dodaj kupon", "dest": "ms_deals:coupons_add"},
                ],
            },
            {
                "heading": "Zestawy kuponów",
                "items": [
                    {"title": "Lista zestawów kuponów", "dest": "ms_deals:coupon_sets_list"},
                    {"title": "Dodaj zestaw kuponów", "dest": "ms_deals:coupon_sets_add"},
                ],
            },
        ],
    },
    "ms_maps": {
        "title": "Mapy i lokalizacje",
        "groups": [
            {
                "heading": None,
                "items": [
                    {"title": "Przegląd", "dest": "ms_maps:maps_overview"},
                ],
            },
            {
                "heading": "Mapy",
                "items": [
                    {"title": "Pokaż aktualną mapę", "dest": "ms_maps:maps_show_current"},
                    {"title": "Edytuj aktualną mapę", "dest": "ms_maps:maps_edit_current"},
                    {"title": "Historia map", "dest": "ms_maps:maps_list"},
                    {"title": "Nowa mapa od zera", "dest": "ms_maps:maps_new"},
                ],
            },
            {
                "heading": "Lokalizacje",
                "items": [
                    {"title": "Lokalizacje produktów", "dest": "ms_maps:product_locations"},
                    {"title": "Auto-przypisanie", "dest": "ms_maps:product_locations_auto"},
                ],
            },
            {
                "heading": "Alejki",
                "items": [
                    {"title": "Lista alejek", "dest": "ms_maps:aisles_list"},
                    {"title": "Dodaj alejkę", "dest": "ms_maps:aisles_add"},
                    {"title": "Dodaj subalejkę", "dest": "ms_maps:subaisles_add"},
                ],
            },
        ],
    },
    "ms_baseline_users": {
        "title": "Użytkownicy",
        "groups": [
            {
                "heading": None,
                "items": [
                    {"title": "Dodaj", "dest": "ms_baseline:users_add"},
                    {"title": "Lista", "dest": "ms_baseline:users_list"},
                    {"title": "Zmień typ", "dest": "ms_baseline:users_change_type"},
                ],
            }
        ],
    },
    "ms_baseline_stores": {
        "title": "Sklepy",
        "groups": [
            {
                "heading": None,
                "items": [
                    {"title": "Dodaj", "dest": "ms_baseline:stores_add"},
                    {"title": "Lista", "dest": "ms_baseline:stores_list"},
                ],
            },
            {
                "heading": "Klucze API kas",
                "items": [
                    {"title": "Dodaj klucz", "dest": "ms_baseline:checkout_api_keys_add"},
                    {"title": "Lista kluczy", "dest": "ms_baseline:checkout_api_keys_list"},
                ],
            },
        ],
    },
}

if MOBISHOPPER_ENV == "dev":
    from mobishopper.settings_dev import *
else:
    from mobishopper.settings_production import *
