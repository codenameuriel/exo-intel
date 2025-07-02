#!/bin/bash

# a script to start both the Celery worker and the Celery Beat scheduler

echo "--- Starting Celery Development Workers ---"

# create directories if they don't exist
mkdir -p logs
mkdir -p run

# activate the virtual environment
source .venv/bin/activate

# start the Celery worker in the background
echo "Starting Celery worker..."
celery -A config worker --loglevel=info > logs/celery_worker.log 2>&1 &

WORKER_PID=$!

# start the Celery Beat scheduler in the background
echo "Starting Celery Beat scheduler..."
celery -A config beat --loglevel=info > logs/celery_beat.log 2>&1 &

BEAT_PID=$!

echo ""
echo "Celery worker and beat scheduler are now running in the background."
echo "Worker PID: $WORKER_PID"
echo "Beat PID: $BEAT_PID"
echo ""
echo "To view logs in real-time, use:"
echo "tail -f logs/celery_worker.log"
echo "tail -f logs/celery_beat.log"
echo ""
echo "To stop the workers, run:"
echo "kill $WORKER_PID $BEAT_PID"
echo "---"