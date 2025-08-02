from .base import *

DEBUG = False

SECRET_KEY = config("SECRET_KEY")

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

STATIC_ROOT = BASE_DIR / "staticfiles"

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
