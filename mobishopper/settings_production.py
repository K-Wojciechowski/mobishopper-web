"""Django settings for mobishopper production."""
import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "mobishopper"),
        "USER": os.getenv("DB_USERNAME", "mobishopper"),
        "PASSWORD": os.getenv("DB_PASSWORD", "mobishopper"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
MOBISHOPPER_MASK_LANDING = True
STATIC_ROOT = "/srv/mobishopper.krzysztofwojciechowski.pl/static"
MEDIA_ROOT = "/srv/mobishopper.krzysztofwojciechowski.pl/media"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.getenv("DJANGO_LOG_PATH", "/tmp/django.log"),
        },
    },
    "loggers": {
        "": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
