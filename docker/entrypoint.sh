#!/usr/bin/env bash
set -euo pipefail

if [ "${ENVIRONMENT}" = "production" ]; then
  exec poetry run gunicorn -c gunicorn.conf.py config.wsgi:application
else
  exec poetry run python3 manage.py runserver 0.0.0.0:8000
fi