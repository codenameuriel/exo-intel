import dj_database_url
import environ

from .base import *

env = environ.Env(
    DEBUG=(bool, False),
)

environ.Env.read_env(
    BASE_DIR / f".env.{env('DJANGO_ENV', default='docker.production')}"
)

DJANGO_LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": DJANGO_LOG_LEVEL, "handlers": ["console"]},
    "django.security": {
        "level": "ERROR",
        "handlers": ["console"],
        "propagate": False,
    },
}

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")

DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        # keep connection alive for 10 minutes
        conn_max_age=600,
    )
}

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = BASE_DIR / "staticfiles"

CELERY_BROKER_URL = env("CELERY_BROKER_URL")

# configure where to store the status and results of completed tasks
# use Redis database #1
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

NASA_TAP_BASE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
