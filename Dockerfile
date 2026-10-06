# ---- build the React app ----
FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ ./
# Same-origin API in production; no VITE_API_URL needed.
RUN npm run build

# ---- run Django + serve the built app ----
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=web /web/dist ./frontend_dist
RUN DJANGO_SECRET_KEY=build python manage.py collectstatic --noinput -v0

# SQLite lives on a volume mounted here.
ENV DATABASE_PATH=/data/db.sqlite3
VOLUME /data
EXPOSE 8000
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
