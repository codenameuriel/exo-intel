from .base import *
import dj_database_url

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

STATIC_ROOT = BASE_DIR / "staticfiles"

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

DATABASES = {
    'default': dj_database_url.config(
        default=config("DATABASE_URL"),
        # keep connection alive for 10 minutes
        conn_max_age=600
    )
}
