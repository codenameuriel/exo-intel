#!/usr/bin/env bash
set -euo pipefail

# Allow Docker and deployment platforms to override the image command.
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

# default to web
ROLE="${PROCESS_TYPE:-web}"             # web | worker | beat | migrate | prepare
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
  migrate)
    exec poetry run python3 manage.py migrate --noinput
    ;;
  prepare)
    exec /usr/local/bin/prepare.sh
    ;;
  *)
    echo "Unknown PROCESS_TYPE: $ROLE" >&2
    exit 1
    ;;
esac
