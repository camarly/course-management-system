# Camarly Thomas — Setup & Implementation Guide

## Your Streams
- Stream A: Infrastructure, Auth, Middleware, Cache, Celery, Frontend, Bonus Features

---

## Phase 1: Your Step-by-Step Implementation Plan

Work through these tasks in order. Every other team member is blocked until Phase 1 is complete and merged to `develop`.

---

### Step 1 — Environment

1. Copy root `.env.example` → `.env`
2. Fill in `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
3. Generate `SECRET_KEY`:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
4. Generate `JWT_SECRET` (repeat the command above — use a different value)
5. Set `CELERY_BROKER_URL=redis://localhost:6379/1`
6. Set `CELERY_RESULT_BACKEND=redis://localhost:6379/2`
7. Set `FLASK_ENV=development`, `FLASK_DEBUG=1`
8. Google OAuth credentials: create a project at console.cloud.google.com, enable the OAuth 2.0 API, create OAuth credentials, copy `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` into `.env`
9. Set `GOOGLE_REDIRECT_URI=http://localhost/api/auth/google/callback`

---

### Step 2 — Docker: Data Services First

```bash
docker compose up -d db redis
docker compose ps          # verify both are healthy
```

---

### Step 3 — Run Migrations

```bash
for f in backend/app/db/migrations/*.sql; do
  docker compose exec -T db mysql \
    -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$f"
done
```

Verify:
```bash
docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES;"
```

Expected: 13 tables + 5 views listed.

---

### Step 4 — Flask Foundation

Files to implement in order:

**`backend/app/config.py`**
- Load every key from `.env` using `python-dotenv`
- Raise `RuntimeError` if any required key is missing on startup

**`backend/app/db/connection.py`**
- Implement `get_connection()` returning a `PyMySQL` connection with `DictCursor`
- Use connection parameters from `config.py`
- This is the only place a MySQL connection is created — every service calls this

**`backend/app/__init__.py`**
- Implement `create_app()`:
  - Create `Flask(__name__)`
  - Load config
  - Register all 13 blueprints from `app/routes/`
  - Add a `/api/health` route returning `{"status": "ok", "env": FLASK_ENV}`
  - Return the app

**`backend/run.py`**
- Already wired — just confirm `from app import create_app` works

Test:
```bash
docker compose up -d api
curl http://localhost/api/health
# Expected: {"status": "ok"}
```

---

### Step 5 — Cache Layer

**`backend/app/cache/client.py`**
- Create a Redis client singleton using `REDIS_URL` from config
- Implement `cache_get(key)` — returns decoded JSON or `None`
- Implement `cache_set(key, value, ttl)` — JSON-encodes and stores
- Implement `cache_del(key)` — single key delete
- Implement `cache_del_pattern(pattern)` — uses `SCAN` + `DEL` (not `KEYS`)

**`backend/app/cache/keys.py`**
- Add key builder functions for each resource, e.g.:
  ```
  COURSES_ALL = "lms:courses:all"
  def course_key(id):     return f"lms:course:{id}"
  def course_members(id): return f"lms:course:{id}:members"
  ```

Test:
```bash
docker compose exec redis redis-cli PING   # PONG
```

---

### Step 6 — Celery

**`backend/app/tasks/celery_app.py`**
- Create `Celery('lms', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)`
- Configure `task_serializer='json'`, `result_serializer='json'`, `accept_content=['json']`

Test (separate terminal):
```bash
docker compose up -d celery_worker
docker compose exec celery_worker celery -A app.tasks.celery_app inspect ping
```

---

### Step 7 — Auth Middleware

**`backend/app/middleware/auth.py`**
- Implement `get_current_user()`:
  - Read `Authorization: Bearer <token>` header
  - Decode with `PyJWT` using `JWT_SECRET`
  - Return `{"id": int, "role": str}`
  - Raise `401` JSON on any failure

**`backend/app/middleware/roles.py`**
- Implement `@require_role(*roles)`:
  - Call `get_current_user()`, store result in `g.current_user`
  - If role not in allowed list → return `403 {"error": "forbidden"}`
  - If valid → pass `current_user` as kwarg to the wrapped function

Share these files with the team immediately — they cannot start coding until this is done.

---

### Step 8 — Auth Routes & Service

**`backend/app/services/auth_service.py`**
- `register(username, email, password, role)` — bcrypt hash, INSERT, return user dict
- `login(username, password)` — fetch user, bcrypt verify, sign JWT, return token
- `google_exchange(code)` — use `Authlib` to exchange code for Google id\_token, UPSERT user, sign JWT
- `admin_create_user(payload)` — INSERT with pre-set role (admin only)

**`backend/app/routes/auth.py`**
- Wire each service function to its route
- Return `{"data": ..., "message": ...}` on success, `{"error": ..., "message": ...}` on failure

---

### Step 9 — User Routes & Service

**`backend/app/services/user_service.py`**
- `get_me(user_id)` — SELECT by ID
- `get_by_id(user_id)` — same, admin use
- `get_all()` — SELECT all users

**`backend/app/routes/users.py`**
- Wire routes with `@require_role` guards

---

### Step 10 — Push Foundation to `develop`

```bash
git checkout -b camarly/auth-infrastructure
git add .
git commit -m "Phase 1: infrastructure, migrations, auth, middleware, cache, celery"
git push origin camarly/auth-infrastructure
```

Open a PR to `develop`. Once merged, notify the team to pull `develop` and begin their stream work.

---

### Step 11 — Share the Contract

Send the team a message (or Slack / WhatsApp) with:

```
get_connection()          → pymysql connection (DictCursor)
get_current_user()        → { id, role }  or raises 401
@require_role('admin')    → decorator, injects current_user kwarg
cache_get(key)            → value or None
cache_set(key, val, ttl)  → None
cache_del(key)            → None
```

They import these from:
```python
from app.db.connection import get_connection
from app.middleware.roles import require_role
from app.cache.client import cache_get, cache_set, cache_del
```

---

## Phase 2 Onwards (after team is unblocked)

- Review team PRs for correct use of the middleware and connection patterns
- Add Redis cache calls to team's GET routes on review
- Wire async Celery task into `grade_service.py` after Carl implements grading
- Implement seed tasks after all tables exist
- Build React frontend last (or in parallel with Phase 3)

---
