#!/bin/bash
set -e

mkdir -p /app/data /app/staticfiles

python manage.py migrate --noinput

# Collect static files for serving via WhiteNoise/gunicorn
python manage.py collectstatic --noinput

exec "$@"
