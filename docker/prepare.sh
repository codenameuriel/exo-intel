#!/usr/bin/env bash
set -euo pipefail

poetry run python3 manage.py migrate --noinput
exec poetry run python3 manage.py import_canonical_data
