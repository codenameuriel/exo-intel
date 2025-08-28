import dj_database_url
import environ

from .base import *

env = environ.Env(
    DEBUG=(bool, True),
)

suffix = env("ENVIRONMENT", default="local")
env_path = BASE_DIR / f".env.{suffix}"
if env_path.exists():
    environ.Env.read_env(env_path)

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
DJANGO_ADMIN_URL = env("DJANGO_ADMIN_URL", default="admin/")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS",
                                default=["http://localhost:8000", "http://127.0.0.1:8000", "http://192.168.1.152:8000"])
SECURE_COOKIES = env("SECURE_COOKIES", default=not DEBUG)
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES

DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600,
    )
}

CELERY_TIMEZONE = env("CELERY_TIMEZONE", default="UTC")

CELERY_BROKER_URL = env("CELERY_BROKER_URL")

# configure where to store the status and results of completed tasks
# use Redis database #1
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

NASA_TAP_BASE_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
