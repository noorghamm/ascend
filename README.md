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

Config lives in `backend/.env` and `frontend/.env` (both created from the
`.env.example` files on first run). To send real email, set the `EMAIL_*`
variables in `backend/.env`.

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
