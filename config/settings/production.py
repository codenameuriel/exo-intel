import dj_database_url

from .base import *

ALLOWED_HOSTS = config(
    "PROD_ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

DATABASES = {
    'default': dj_database_url.config(
        default=config("DATABASE_URL"),
        # keep connection alive for 10 minutes
        conn_max_age=600
    )
}

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

SECRET_KEY = config("PROD_SECRET_KEY")

STATIC_ROOT = BASE_DIR / "staticfiles"