#!/bin/sh
set -e
mkdir -p "$(dirname "${DATABASE_PATH:-/data/db.sqlite3}")"
python manage.py migrate --noinput -v0
exec "$@"
