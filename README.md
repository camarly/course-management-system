# Course Management System (CMS) — COMP3161

Full-stack Course Management System built for COMP3161 — Database Systems. Flask + raw SQL on MySQL 8, Redis cache, Celery for async tasks, React + Vite for the UI, nginx in front, all in Docker.

> **Live:** https://cms-uwi.up.railway.app — single combined image deployed on Railway, MySQL + Redis as Railway plugins, schema auto-migrated on startup, fully seeded to spec (1 admin + 50 lecturers + 100,000 students; 200 courses; 300,000 enrollments; 585 assignments; 11,700 submissions + grades).
>
> **Submission artifacts:** ERD diagram and per-member contributions PDF are submitted separately. `CONTRIBUTIONS.md` in this repo is the source for the contributions section.

---

## What's in the box

| Layer | Tech | Notes |
|---|---|---|
| API | Flask, **raw SQL only** (no ORM) | All DB calls go through `app/db/connection.py::get_connection()` |
| DB | MySQL 8 | 14 numbered migrations auto-run by the container on first start |
| Auth | JWT (PyJWT) + bcrypt | `@require_role(...)` decorator gates every protected route |
| Cache | Redis 7 | All five report endpoints cached with a medium TTL |
| Async | Celery + Redis broker | Grade-recalc task fires after every grade insert |
| Frontend | React + Vite | Auth, courses, forums, assignments, grades, calendar, content, reports |
| Reverse proxy | nginx | Serves the React build on port 80 and proxies `/api/*` to Flask |
| Tests | pytest | 84 passing tests, in-memory MySQL + Redis fakes (no live services needed) |
| CI | GitHub Actions | Lint + test on every PR to `main` |

---

## Functional overview — what each part does

### 1. Auth
Self-register as student or lecturer; admin can create accounts of any role. Login returns a JWT (`data.token`) that's attached as `Authorization: Bearer <token>` to every protected request.

### 2. Courses + Enrollment
Admins create courses and assign lecturers (one lecturer per course; 5-course cap per lecturer enforced). Students self-enroll, capped at 6 active courses; duplicate enrollment returns 409.

### 3. Course content
Lecturers organise material into ordered sections, each containing typed content items (slides / video / link / etc.). Anyone enrolled can read.

### 4. Assignments + Submissions + Grades
Lecturers post assignments with due date and weight. Students upload one submission per assignment (409 on duplicate). Lecturers grade; on insert, a Celery task recomputes the student's overall average asynchronously into `student_averages`.

### 5. Forums + Threads + Replies
Lecturers/admins create forums on a course. Anyone enrolled can open threads and post replies. Replies nest to unlimited depth — `GET /api/threads/<id>` returns the full tree in one call.

### 6. Calendar
Lecturers post events on a course (date + optional time). `GET /api/students/<id>/events?date=YYYY-MM-DD` returns everything the student has across all enrolled courses on that day.

### 7. Reports (admin)
Five admin-only reports backed by SQL views (migration `014_create_views.sql`) and cached in Redis:

- Courses with ≥ 50 enrolled students
- Students enrolled in ≥ 5 courses
- Lecturers teaching ≥ 3 courses
- Top 10 most-enrolled courses
- Top 10 students by average grade

---

## Trying the deployed Railway instance

The fastest way to grade the API is via the **Postman collection in `postman/`**. Two minutes to import, then everything is auto-authed:

1. Postman → **File → Import** → drop in `postman/CMS_API.postman_collection.json` and `postman/environments/railway.postman_environment.json`.
2. Top-right environment dropdown → pick **CMS — Railway**. Both `base_url` (the Railway URL) and the seeded admin credentials (`admin` / `password123`) are pre-filled.
3. Open any request (start with **Health → Health check**) and Send.

The collection's pre-request script logs in automatically using `test_username` / `test_password` from the active environment and stores the JWT in `jwt_token`. Every protected request inherits a Bearer auth set at the collection level. See `postman/README.md` for the full walkthrough.

---

## Running locally (Docker)

You only need **Docker Desktop** + **Git**. No Python, Node, MySQL, or Redis on the host.

```bash
git clone git@github.com:camarly/course-management-system.git
cd course-management-system
cp .env.example .env             # defaults are wired for local Docker — no edits needed
docker compose up --build -d
```

Six services come up:

| Service | URL |
|---|---|
| nginx (serves React build + proxies `/api/*`) | http://localhost |
| Vite dev server (HMR, dev only) | http://localhost:5173 |
| Flask API | internal — reach via http://localhost/api |
| MySQL 8 | localhost:3306 |
| Redis | internal only |
| Celery worker | background, no port |

Migrations auto-run on first start (every `.sql` in `backend/app/db/migrations/`).

Health check:

```bash
curl http://localhost/api/health
# → {"status": "ok", "env": "development"}
```

> **Note for Postman against local:** in `postman/environments/local.postman_environment.json`, the placeholder `base_url` is `http://localhost:5000`. Change it to `http://localhost` (port 80) — the API container's port 5000 is internal only; nginx is the externally reachable side.

---

## Test credentials

After running the seed pipeline (below), the following accounts exist. **Every seeded user has the same password: `password123`.**

| Role | Username pattern | Example | Password |
|---|---|---|---|
| Admin | `admin` | `admin` | `password123` |
| Lecturer | `lecturer_<n>` | `lecturer_0`, `lecturer_1`, … | `password123` |
| Student | `student_<n>` | `student_0`, `student_1`, … | `password123` |

Counts after seeding: 1 admin, 50 lecturers (`lecturer_0`–`lecturer_49`), 100,000 students (`student_0`–`student_99999`).

> Login uses the **`username`** field (not email). Emails are `<username>@lms.local` but the API doesn't accept email as the login identifier.

To register a fresh account instead:

```bash
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "secret123", "role": "student"}'
```

---

## Seeding the database

Required by the project spec (≥ 100,000 students, ≥ 200 courses, all enrollment caps enforced). Run inside the api container:

```bash
docker compose exec api python -m seed.seed_runner
```

Takes a few minutes. Output reports counts at every stage. After it finishes, the test credentials above are valid.

---

## Running the test suite

All tests run **inside the api container** — no host toolchain.

```bash
docker compose exec api pytest -v
# → 84 passed
```

Subsets:

```bash
docker compose exec api pytest tests/test_courses.py -v
docker compose exec api pytest tests/test_courses.py::TestCreateCourse -v
```

---

## Everyday Docker commands

| Action | Command |
|---|---|
| Start everything | `docker compose up -d` |
| Tail API logs | `docker compose logs -f api` |
| Tail Celery logs | `docker compose logs -f celery_worker` |
| Restart API after code change | `docker compose restart api` |
| MySQL shell | `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db` |
| Redis shell | `docker compose exec redis redis-cli` |
| Stop stack, keep data | `docker compose down` |
| Stop stack, wipe DB volume | `docker compose down -v` |

---

## Auth flow in detail

1. **Register or use a seeded account.**
   ```bash
   curl -X POST http://localhost/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "password123"}'
   ```
2. **Capture the token** returned at `data.token` in the response.
3. **Attach it** as `Authorization: Bearer <token>` on every protected request.
   ```bash
   curl http://localhost/api/users/me -H "Authorization: Bearer eyJ..."
   ```

Tokens expire after 1 hour (`JWT_EXPIRY_HOURS` in `.env`). The Postman collection refreshes automatically — clear `jwt_token` in the active environment and the next request re-logs-in.

---

## Project structure

```
course-management-system/
├── backend/                Flask API + Celery worker
│   ├── app/
│   │   ├── routes/         13 blueprints — auth, users, courses, enrollments,
│   │   │                   calendar, content, forums, threads, replies,
│   │   │                   assignments, submissions, grades, reports
│   │   ├── services/       Business logic, raw SQL via get_connection()
│   │   ├── middleware/     @require_role decorator
│   │   ├── cache/          Redis client + key builders
│   │   ├── tasks/          Celery app + tasks (grade recalc, etc.)
│   │   └── db/migrations/  14 numbered SQL files, auto-run by MySQL
│   ├── seed/               Bulk seeding to spec (100k students, 200 courses)
│   └── tests/              pytest suite (84 passing, in-memory fakes)
├── frontend/               React + Vite SPA
├── nginx/                  Reverse proxy serving the React build + /api/*
├── postman/                Collection + environments + README
└── .github/workflows/      CI (lint + test) and Railway deploy
```

---

## Submission

- **Code repository:** this repo (`main` branch).
- **ERD + contributions PDF:** submitted separately. `CONTRIBUTIONS.md` in this repo is the source for the contributions section.
- **Postman collection:** `postman/CMS_API.postman_collection.json` (also usable against the Railway URL via the Railway environment).
- **Live URL:** see top of this file.
