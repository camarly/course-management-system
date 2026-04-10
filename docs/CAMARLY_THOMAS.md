# Camarly Thomas — Phase 1 Implementation Guide

## Your Streams
- Stream A: Infrastructure, Auth, Middleware, Cache, Celery, Frontend, Bonus Features

---

## What is already done

These files are **implemented and ready** — do not rewrite them:

| File | Status |
|---|---|
| `backend/app/config.py` | Loads `.env`, validates required vars, exports constants |
| `backend/app/db/connection.py` | `get_connection()` returns PyMySQL DictCursor |
| `backend/app/middleware/auth.py` | `get_current_user()` decodes JWT from Authorization header |
| `backend/app/middleware/roles.py` | `@require_role(*roles)` decorator, injects `current_user` kwarg |
| `backend/app/__init__.py` | `create_app()` factory, registers 13 blueprints, `/api/health` |
| `backend/run.py` | Entry point — `from app import create_app` |
| All 14 migration files | Schema complete — 13 tables + 5 views |
| `docker-compose.yml` | 6 services: nginx, api, db, redis, celery_worker, frontend |
| `.env.example` | Template with Docker service names |
| `nginx/nginx.conf` | Reverse proxy `/api/*` to Flask |
| `.github/workflows/ci.yml` | Backend tests + frontend build on push |

---

## Phase 1: Step-by-Step Implementation (remaining work)

Work through these steps in order. Every other team member is blocked until Phase 1 is complete and merged to `develop`.

---

### Step 1 — Environment Setup

Your `.env` is already configured. Verify it has Docker service names (not localhost):

```
DB_HOST=db
DB_PORT=3306
DB_NAME=lms_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

If you need to run Flask **outside** Docker (bare-metal debugging), temporarily change `db`/`redis` to `localhost`. Switch back before committing.

Generate secrets (already done, but for reference):
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

### Step 2 — Boot Data Services & Verify

```bash
docker compose up -d db redis
docker compose ps          # both should show "healthy" / "running"
```

Verify MySQL:
```bash
docker compose exec db mysql -uDragon -ppassword10 lms_db -e "SELECT 1;"
```

Verify Redis:
```bash
docker compose exec redis redis-cli PING   # expect: PONG
```

---

### Step 3 — Run Migrations

On **first start** with an empty `mysql_data` volume, MySQL automatically runs every `.sql` file from the migrations directory (mounted to `/docker-entrypoint-initdb.d`).

To manually run on an existing database:
```bash
set -a && source .env && set +a

for f in backend/app/db/migrations/*.sql; do
  docker compose exec -T db mysql -uDragon -ppassword10 lms_db < "$f"
done
```

All migrations use `CREATE TABLE IF NOT EXISTS` / `CREATE OR REPLACE VIEW` — re-running is safe.

Verify:
```bash
docker compose exec db mysql -uDragon -ppassword10 lms_db -e "SHOW TABLES;"
```

Expected: 13 tables + 5 views (18 rows).

---

### Step 4 — Implement Cache Layer

#### `backend/app/cache/client.py`

Replace the stub. You need to implement these functions:

| Function | What it does | Key details |
|---|---|---|
| `cache_get(key)` | Fetch from Redis, return decoded value or `None` | Use `json.loads()` on the raw string |
| `cache_set(key, value, ttl)` | JSON-encode, store with TTL in seconds | Use `setex(key, ttl, json_string)` |
| `cache_del(key)` | Delete a single key | Call on every mutation (POST/PUT/DELETE) |
| `cache_del_pattern(pattern)` | Delete all keys matching a glob | Use `SCAN` + `DELETE`, **not** `KEYS` |

**What to look up:**
- `redis.from_url(REDIS_URL, decode_responses=True)` — creates a client with connection pooling. `decode_responses=True` means values come back as `str` not `bytes`
- Create one client at module level (singleton) — don't create a new connection per request
- Wrap every Redis call in `try/except redis.RedisError` — cache failures should log a warning and return `None`, never crash the app
- `json.dumps(value, default=str)` handles `datetime` and `Decimal` objects without errors

#### `backend/app/cache/keys.py`

Add key builder functions below the existing TTL constants. Convention: `lms:<resource>:<id>`.

What you need:
- Static keys: `COURSES_ALL`, `USERS_ALL`
- Builder functions for: `course_key(id)`, `course_members_key(id)`, `course_forums_key(id)`, `course_events_key(id)`, `course_assignments_key(id)`, `course_sections_key(id)`, `forum_threads_key(id)`, `thread_key(id)`, `user_key(id)`, `student_courses_key(id)`, `lecturer_courses_key(id)`, `student_grades_key(id)`, `assignment_key(id)`, `assignment_submissions_key(id)`
- Report keys: one constant per report endpoint (5 total)

Each builder is a one-line f-string. The point is that everyone uses the same key for the same resource.

**Test:**
```bash
docker compose up -d api
docker compose exec api python -c "
from app.cache.client import cache_set, cache_get, cache_del
cache_set('test:key', {'hello': 'world'}, 30)
print(cache_get('test:key'))
cache_del('test:key')
print(cache_get('test:key'))
print('Cache OK')
"
```

---

### Step 5 — Implement Celery App

#### `backend/app/tasks/celery_app.py`

Replace the stub. You need to create a `celery_app` instance — this is what the docker-compose command references (`celery -A app.tasks.celery_app worker`).

**What to implement:**
- `celery_app = Celery("lms", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)`
- Configure: `task_serializer="json"`, `result_serializer="json"`, `accept_content=["json"]`

**What to look up:**
- Import `CELERY_BROKER_URL` and `CELERY_RESULT_BACKEND` from `app.config`
- `celery_app.conf.update(...)` to set config
- `celery_app.autodiscover_tasks(["app.tasks"])` — auto-finds `@celery_app.task` functions in the tasks package
- Optional but good: `task_acks_late=True` (acknowledge after completion, prevents task loss on crash), `worker_prefetch_multiplier=1` (fair task distribution)

**Test:**
```bash
docker compose up -d celery_worker
docker compose logs celery_worker --tail 20
# Should see: "celery@... ready" and "Connected to redis://redis:6379/1"
```

---

### Step 6 — Implement Auth Service

#### `backend/app/services/auth_service.py`

This is the business logic for authentication. Routes will call these functions.

**Functions to implement:**

| Function | Input | What it does | Returns |
|---|---|---|---|
| `create_token(user_id, role)` | int, str | Sign a JWT with `sub`, `role`, `exp` | token string |
| `register(username, email, password, role)` | strings | Validate role is student/lecturer, hash password with bcrypt, INSERT into users, check for duplicates | user dict |
| `login(username, password)` | strings | SELECT user by username, verify bcrypt hash, sign JWT | `{"token": ..., "user": {...}}` |
| `admin_create_user(username, email, password, role)` | strings | Same as register but allows admin role | user dict |

**What to look up:**
- `bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())` — returns bytes, `.decode()` before storing
- `bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))` — returns `True`/`False`
- `jwt.encode(payload, JWT_SECRET, algorithm="HS256")` — returns a string in PyJWT 2.x
- `datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS)` for token expiry
- Import config values: `JWT_SECRET`, `JWT_EXPIRY_HOURS` from `app.config`
- Raise `ValueError` on failures (duplicate user, bad credentials, invalid role) — routes catch these and return the right HTTP status

**SQL pattern for all services:**
```python
conn = get_connection()
try:
    with conn.cursor() as cur:
        cur.execute("SELECT ... WHERE col = %s", (param,))
        row = cur.fetchone()  # dict or None
        # For writes:
        cur.execute("INSERT INTO ... VALUES (%s, %s)", (a, b))
        conn.commit()
        new_id = cur.lastrowid
finally:
    conn.close()
```

**Rules:**
- Always `conn.close()` in `finally`
- Always `conn.commit()` after INSERT/UPDATE/DELETE
- Use `%s` placeholders — **never** f-strings or `.format()` in SQL
- `cur.fetchone()` returns `dict` or `None`; `cur.fetchall()` returns `list[dict]`

**Note on Google OAuth:** Skipped for now. The `google/login` and `google/callback` routes can return `501 Not Implemented` for now. Add Google OAuth as a bonus in Phase 4 if time allows.

---

### Step 7 — Implement Auth Routes

#### `backend/app/routes/auth.py`

Wire each service function to its HTTP endpoint. The blueprint and url_prefix are already defined.

**Endpoints to implement:**

| Route | Method | Auth? | What it does |
|---|---|---|---|
| `/register` | POST | No | Read JSON body, validate required fields (username, email, password, role), call `register()`, return 201 |
| `/login` | POST | No | Read JSON body, call `login()`, return 200 |
| `/google/login` | GET | No | Return 501 for now (placeholder) |
| `/google/callback` | GET | No | Return 501 for now (placeholder) |
| `/admin/create-user` | POST | Yes (admin) | `@require_role("admin")`, read body, call `admin_create_user()`, return 201 |

**What to look up:**
- `request.get_json(silent=True)` — returns `None` instead of 400 if body isn't JSON
- Validate required fields exist before calling the service
- Catch `ValueError` from service functions and return appropriate HTTP codes (409 for duplicates, 401 for bad credentials, 400 for validation)

**Response envelope (used on every endpoint in the project):**
```python
# Success
jsonify({"data": result, "message": "Registration successful"}), 201

# Error
jsonify({"error": "conflict", "message": "Username already taken"}), 409
```

---

### Step 8 — Implement User Service & Routes

#### `backend/app/services/user_service.py`

Three simple SELECT queries:

| Function | SQL | Returns |
|---|---|---|
| `get_me(user_id)` | `SELECT id, username, email, role, created_at FROM users WHERE id = %s` | dict or None |
| `get_by_id(user_id)` | Same query (admin use) | dict or None |
| `get_all()` | `SELECT id, username, email, role, created_at FROM users ORDER BY id` | list[dict] |

Never return `password_hash` in any query.

#### `backend/app/routes/users.py`

| Route | Method | Auth | Role | What it does |
|---|---|---|---|---|
| `/me` | GET | Yes | any | `@require_role("admin", "lecturer", "student")`, call `get_me(current_user["id"])` |
| `/<int:user_id>` | GET | Yes | admin | `@require_role("admin")`, call `get_by_id(user_id)` |
| `/` (empty) | GET | Yes | admin | `@require_role("admin")`, call `get_all()` |

Return 404 if `get_me` or `get_by_id` returns `None`.

**Note on route parameter naming:** Flask uses `<int:user_id>` in the URL rule. This becomes a function argument. The `@require_role` decorator also injects `current_user` as a kwarg. So your function signature looks like: `def handle_get_user(user_id, current_user):`

---

### Step 9 — Full Stack Verification

```bash
docker compose up --build -d
docker compose ps     # all 6 services running
```

**Test sequence:**

```bash
# 1. Health check
curl http://localhost/api/health

# 2. Register a student
curl -s -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"teststudent","email":"student@test.com","password":"secret123","role":"student"}'

# 3. Login
curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teststudent","password":"secret123"}'
# Copy the token from the response

# 4. Test /me with token
TOKEN="<paste>"
curl -s http://localhost/api/users/me -H "Authorization: Bearer $TOKEN"

# 5. Test role guard (student accessing admin route — should 403)
curl -s http://localhost/api/users -H "Authorization: Bearer $TOKEN"

# 6. Create an admin user directly (register only allows student/lecturer)
docker compose exec api python -c "
import bcrypt
from app.db.connection import get_connection
conn = get_connection()
try:
    h = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode()
    with conn.cursor() as cur:
        cur.execute('INSERT INTO users (username, email, password_hash, role) VALUES (%s,%s,%s,%s)',
                    ('admin', 'admin@lms.local', h, 'admin'))
        conn.commit()
        print('Admin created, id:', cur.lastrowid)
finally:
    conn.close()
"

# 7. Login as admin, test admin routes
curl -s -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 8. Cache test
docker compose exec api python -c "
from app.cache.client import cache_set, cache_get, cache_del
cache_set('test:key', {'hello': 'world'}, 30)
print(cache_get('test:key'))
cache_del('test:key')
print(cache_get('test:key'))
print('Cache OK')
"

# 9. Celery test
docker compose logs celery_worker --tail 10
```

**Phase 1 exit criteria (all must pass):**
- `POST /api/auth/register` returns 201 with a JWT
- `POST /api/auth/login` returns 200 with a JWT
- `GET /api/users/me` returns 200 with a valid token, 401 without
- `GET /api/users` returns 403 for non-admin, 200 for admin
- `docker compose up --build` starts all services without errors
- Redis cache_get/set/del work
- Celery worker starts without crashing

---

## Shared Contract (what the team imports from your code)

```python
from app.db.connection import get_connection       # MySQL DictCursor connection
from app.middleware.roles import require_role       # @require_role('admin') decorator
from app.cache.client import cache_get, cache_set, cache_del
```

`require_role` injects `current_user = {"id": int, "role": str}` as a kwarg.

---

## JWT Authentication — Reference

### Token payload
```json
{"sub": 42, "role": "student", "exp": 1712700000}
```

| Field | Type | Description |
|---|---|---|
| `sub` | int | User ID from `users` table |
| `role` | string | `admin`, `lecturer`, or `student` |
| `exp` | int | Unix timestamp, expires after `JWT_EXPIRY_HOURS` |

### Quick token generation for testing
```bash
docker compose exec api python -c "
from app.services.auth_service import create_token
print('admin:', create_token(user_id=1, role='admin'))
print('student:', create_token(user_id=2, role='student'))
"
```

### Postman setup
After logging in, copy the token and set it as the environment variable `jwt_student` (or `jwt_lecturer`, `jwt_admin`). Configure the collection's Authorization tab to use `Bearer Token` with `{{jwt_student}}`.

---

## Phase 2 Onwards (after team is unblocked)

- Review team PRs for correct use of the middleware and connection patterns
- Add Redis cache calls to team's GET routes on review
- Wire async Celery task into `grade_service.py` after Carl implements grading
- Implement seed tasks after all tables exist (Phase 3)
- Build React frontend last (Phase 4, concurrent with Phase 3)

---
