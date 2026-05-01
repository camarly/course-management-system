# Postman — CMS API

A ready-to-import Postman collection covering every route registered on the Flask app, with two environments (Local and Railway) and a pre-request script that auto-issues a JWT.

## Files

| Path | Purpose |
|---|---|
| `CMS_API.postman_collection.json` | The full collection — 40 requests across 14 folders. |
| `environments/local.postman_environment.json` | Points at `http://localhost:5000`. |
| `environments/railway.postman_environment.json` | Points at the deployed Railway URL (you fill it in). |

## Import

1. Open Postman → **File → Import** (or the top-left **Import** button).
2. Drag in the three JSON files above (collection + both environment files).
3. In the top-right environment dropdown, pick either **CMS — Local** or **CMS — Railway**.

## Set the Railway URL

Before using the **CMS — Railway** environment, replace the placeholder:

1. In Postman's left sidebar click **Environments → CMS — Railway**.
2. Find the `base_url` row.
3. Change `{{RAILWAY_URL}}` to your actual URL, e.g.
   `https://cms-api-production.up.railway.app`
   - No trailing slash.
   - Use `https://`, not `http://`.
4. Click **Save**.

The Railway URL is the public address of the API service. If your Railway project also runs nginx in front of the API, point `base_url` at the nginx service URL instead — both work, since nginx proxies `/api/*` to the API container.

## How JWT auth works

Auth is fully automatic — you don't paste tokens anywhere.

1. The collection has a top-level **Pre-request Script** that runs before every request.
2. If the active environment has no `jwt_token` set, the script issues `POST {{base_url}}/api/auth/login` with the body
   ```json
   { "username": "{{test_username}}", "password": "{{test_password}}" }
   ```
3. The token returned under `data.token` is stored in the active environment's `jwt_token` variable.
4. Every non-public request inherits the collection-level **Bearer Token** auth, which sends `Authorization: Bearer {{jwt_token}}`.

To force a fresh login (e.g. token expired, or to switch users): in the active environment, clear the `jwt_token` value and save.

Public routes (`POST /api/auth/login`, `POST /api/auth/register`, `GET /api/health`) are configured per-request as **No Auth** so the bearer header isn't attached.

## Switching between Local and Railway

Top-right environment dropdown — pick one. Each environment carries its own `base_url`, `test_username`, `test_password`, and `jwt_token`, so switching does not leak credentials or tokens between environments.

## Test credentials

Both environment files default to:

| Key | Value |
|---|---|
| `test_username` | `test@example.com` |
| `test_password` | `testpassword123` |

> **Important — note on the username field:** the spec for these env files used `test_email` as the variable name, but the API's `POST /api/auth/login` endpoint expects a JSON field literally named `username` (see `backend/app/routes/auth.py`). To avoid silent confusion, the variable here is named `test_username`. Set it to whatever username you registered with — it can look like an email (the column is `VARCHAR(50)`, no email validation).

You'll need an account that exists in your DB. Either:

- **Local:** run the seed script (`docker compose exec api python -m seed.run`) and use one of the seeded credentials, or register a fresh account via `POST /api/auth/register` from the **Auth** folder.
- **Railway:** register via the **Register** request once after deploy, then update `test_username` / `test_password` in the Railway environment to match.

## Folder layout

The collection is grouped by blueprint:

- **Health** · liveness probe
- **Auth** · register, login, admin-create-user
- **Users** · me, list, get-by-id
- **Courses** · CRUD, members, assign lecturer, by-student, by-lecturer
- **Enrollments** · student self-enroll
- **Calendar** · course events + per-student-on-date
- **Content** · sections + items
- **Forums** · per-course
- **Threads** · per-forum + nested-reply tree
- **Replies** · top-level + nested
- **Assignments** · CRUD per course
- **Submissions** · submit, list, student grades
- **Grades** · record (triggers Celery recalc)
- **Reports (admin)** · all five SQL-view-backed reports
