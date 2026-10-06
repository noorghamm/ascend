# Ascend

*Find your level.*

A study-buddy board for the University of Glasgow library. Post when you're in,
which zone you're on (green / amber / red), which level, and how long you're
staying, so people who like studying with company can find each other.

No accounts. Posts go live after you click a link sent to your student email,
and expire on their own. The same email has a "remove my post" link.

**Stack:** Django REST Framework (API, SQLite) · React + Vite (frontend)

## Run it

```bash
./dev.sh
```

That creates a virtualenv, installs everything, runs migrations, and starts
both servers. Open http://localhost:5173. Verification emails are printed to
the same terminal; click the `/verify/...` link to go live.

Config lives in `backend/.env` (created from `.env.example` on first run).
The frontend talks to `/api`, which Vite proxies to Django in development.

## Email

Three modes, picked by what's set in `backend/.env`:

| Set                | Sends via                              |
| ------------------ | -------------------------------------- |
| nothing            | printed to the terminal (development)  |
| `RESEND_API_KEY`   | [Resend](https://resend.com) HTTP API  |
| `EMAIL_HOST` etc.  | plain SMTP                             |

For Resend: sign up, verify a domain, create an API key, then set
`RESEND_API_KEY` and `DEFAULT_FROM_EMAIL=Ascend <ascend@yourdomain>`.

## Deploy

One container runs Django under gunicorn and serves the built React app.
SQLite lives on a volume at `/data`.

```bash
# Any VPS with Docker:
cp backend/.env.example backend/.env   # fill in SECRET_KEY, URLs, email
docker compose up -d --build           # http://<host>:8000, put Caddy/nginx in front for TLS

# Fly.io:
fly launch --copy-config --no-deploy
fly volumes create ascend_data --size 1 --region lhr
fly secrets set DJANGO_SECRET_KEY=$(openssl rand -hex 32) RESEND_API_KEY=re_... DEFAULT_FROM_EMAIL="Ascend <ascend@yourdomain>"
fly deploy
```

Edit the hostnames in `fly.toml` to match your app name. For a VPS set
`BACKEND_URL`, `FRONTEND_URL` and `DJANGO_ALLOWED_HOSTS` in `backend/.env`
to your real domain.

## Useful commands

```bash
backend/.venv/bin/python backend/manage.py test            # API tests
backend/.venv/bin/python backend/manage.py purge_sessions  # delete expired / stale rows
backend/.venv/bin/python backend/manage.py createsuperuser # for /admin/
cd frontend && npm run lint
```

## API

| Method | Path                     | What                                   |
| ------ | ------------------------ | -------------------------------------- |
| GET    | `/api/sessions/`         | Live, verified posts (newest first)    |
| POST   | `/api/sessions/`         | Create a post; sends the verify email  |
| GET    | `/verify/<token>/`       | Marks the post live, redirects to app  |
| GET    | `/remove/<token>/`       | Deletes the post, redirects to app     |

Rules: `@student.gla.ac.uk` emails only, 30 min to 6 h in half-hour steps,
level must belong to the chosen zone, one live post per email.

**Status:** work in progress — my first React project, built to solve a
problem I actually have.
