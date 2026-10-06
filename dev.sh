#!/usr/bin/env bash
# Starts the Django API and the Vite dev server together. Ctrl-C stops both.
set -euo pipefail
cd "$(dirname "$0")"

# --- backend ---
if [ ! -d backend/.venv ]; then
  echo "▸ creating backend/.venv"
  python3 -m venv backend/.venv
fi
backend/.venv/bin/pip install -q -r backend/requirements.txt
[ -f backend/.env ] || cp backend/.env.example backend/.env
backend/.venv/bin/python backend/manage.py migrate -v0

# --- frontend ---
[ -f frontend/.env ] || cp frontend/.env.example frontend/.env
if [ ! -d frontend/node_modules ]; then
  echo "▸ installing frontend deps"
  (cd frontend && npm install --silent)
fi

trap 'kill 0' EXIT INT TERM
(cd backend && exec .venv/bin/python manage.py runserver 127.0.0.1:8000) &
(cd frontend && exec npm run dev -- --host) &

echo
echo "  Ascend is up:"
echo "    board  →  http://localhost:5173"
echo "    api    →  http://localhost:5173/api/sessions/  (proxied to :8000)"
echo "    admin  →  http://127.0.0.1:8000/admin/"
echo "  Verify emails print in this terminal (no SMTP configured)."
echo
wait
