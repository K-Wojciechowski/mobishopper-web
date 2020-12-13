"""Django settings for mobishopper development."""
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.path.join(BASE_DIR, "db.sqlite3")}}
MOBISHOPPER_MASK_LANDING = False
MEDIA_ROOT = "media/"


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "stderr": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["stderr"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
