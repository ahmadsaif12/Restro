# handle_my_restore

## Dev (Docker)

1. Create/update env file:
   - `cp .env.example .env`
2. Start:
   - `make up` (or `docker compose --env-file .env up --build`)
3. Open:
   - `http://localhost:8000/admin/`

## Auth API

Base path: `/api/auth/`

- `POST /register/` `{ "email": "...", "full_name": "...", "password": "...", "role": "waiter|owner|cashier" }`
- `POST /login/` `{ "email": "...", "password": "..." }` -> JWT `access` + `refresh`
- `POST /logout/` `{ "refresh": "..." }` (blacklists refresh token)
- `POST /token/refresh/` `{ "refresh": "..." }`
- `GET /profile/` (Authorization: `Bearer <access>`)
- `GET /profile/<user_id>/` (Authorization: `Bearer <access>`)
- `POST /password/forgot/` `{ "email": "...", "frontend_url": "https://..." (optional) }`
- `POST /password/reset/confirm/` `{ "uid": "...", "token": "...", "new_password": "..." }`

## API Docs (Swagger)

- Swagger UI: `GET /api/docs/`
- OpenAPI schema: `GET /api/schema/`
- ReDoc: `GET /api/redoc/`

## Admin Styling

Admin CSS override lives in `static/admin/custom.css` and is loaded via `templates/admin/base_site.html`.

## Celery (Worker + Beat)

Docker compose services included:
- `worker`: Celery worker
- `beat`: Celery beat (DB scheduler via `django-celery-beat`)

Example task: `apps.autho.tasks.ping`

## Pre-commit

- Install and run:
  - `pre-commit install`
  - `pre-commit run --all-files`
