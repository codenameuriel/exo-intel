#!/usr/bin/env bash
set -euo pipefail

# default to web
ROLE="${PROCESS_TYPE:-web}"             # web | worker | beat
ENVIRONMENT="${ENVIRONMENT:-local}"     # local | production
CELERY_BEAT_SCHEDULE_FILE="${CELERY_BEAT_SCHEDULE_FILE:-/app/run/celerybeat-schedule}"

mkdir -p /app/run /app/logs

echo "[entrypoint] ROLE=${ROLE} ENVIRONMENT=${ENVIRONMENT}"

case "$ROLE" in
  web)
    if [ "$ENVIRONMENT" = "production" ]; then
      exec poetry run gunicorn -c gunicorn.conf.py config.wsgi:application
    else
      exec poetry run python3 manage.py runserver 0.0.0.0:8000
    fi
    ;;
  worker)
    # lean worker configuration for small RAM plan in Render
    if [ "${CELERY_PROFILE:-}" = "Render" ]; then
      exec poetry run celery -A config worker --loglevel=info \
      --pool=solo -Ofair --without-gossip --without-mingle --without-heartbeat
    else
      exec poetry run celery -A config worker --loglevel=info
    fi
    ;;
  beat)
    exec poetry run celery -A config beat --loglevel=info --schedule="${CELERY_BEAT_SCHEDULE_FILE}"
    ;;
  *)
    echo "Unknown PROCESS_TYPE: $ROLE" >&2
    exit 1
    ;;
esac