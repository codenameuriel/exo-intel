#!/bin/bash
set -euo pipefail

echo "--- Starting Celery Development Workers ---"

# create directories if they don't exist
mkdir -p logs run

# defaults
#: "${CELERY_WORKER_LOG_FILE:=logs/celery_worker.log}"
#: "${CELERY_BEAT_LOG_FILE:=logs/celery_beat.log}"
#: "${CELERY_BEAT_SCHEDULE_FILE:=run/celerybeat-schedule}"
#: "${DJANGO_SETTINGS_MODULE:?DJANGO_SETTINGS_MODULE must be set (put it in your .env.*)}"

# start the Celery worker in the background
echo "Starting Celery worker...(log at ${CELERY_WORKER_LOG_FILE})"

celery -A config worker --loglevel=info \
  --pidfile=run/celery_worker.pid \
  &>>"${CELERY_WORKER_LOG_FILE}" &

WORKER_PID=$!

# start the Celery Beat scheduler in the background
echo "Starting Celery Beat scheduler...(log at ${CELERY_BEAT_LOG_FILE})"

celery -A config beat --loglevel=info \
  --schedule="${CELERY_BEAT_SCHEDULE_FILE}" \
  --pidfile=run/celery_beat.pid \
  &>>"${CELERY_BEAT_LOG_FILE}" &

BEAT_PID=$!

echo ""
echo "Celery worker and beat scheduler are now running in the background."
echo "Worker PID: $WORKER_PID"
echo "Beat PID: $BEAT_PID"
echo ""
echo "To view logs in real-time, use:"
echo "tail -f ${CELERY_WORKER_LOG_FILE}"
echo "tail -f ${CELERY_BEAT_LOG_FILE}"
echo ""
echo "To stop the workers, run:"
echo "kill \$(cat run/celery_worker.pid) \$(cat run/celery_beat.pid)"
echo "---"