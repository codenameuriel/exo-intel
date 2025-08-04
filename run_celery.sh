#!/bin/bash

# a script to start both the Celery worker and the Celery Beat scheduler

echo "--- Starting Celery Development Workers ---"

#load .env vars into terminal session
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

# create directories if they don't exist
mkdir -p logs
mkdir -p run

# activate the virtual environment
source .venv/bin/activate

# start the Celery worker in the background
echo "Starting Celery worker...(log at ${CELERY_WORKER_LOG_FILE})"
celery -A config worker --loglevel=info > "${CELERY_WORKER_LOG_FILE}" 2>&1 &
# save worker pid
echo $! > run/celery_worker.pid

# start the Celery Beat scheduler in the background
echo "Starting Celery Beat scheduler...(log at ${CELERY_BEAT_LOG_FILE})"
celery -A config beat --loglevel=info --schedule="${CELERY_BEAT_SCHEDULE_FILE}" > "${CELERY_BEAT_LOG_FILE}" 2>&1 &
echo $! > run/celery_beat.pid

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