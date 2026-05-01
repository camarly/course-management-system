# Contributions — COMP3161 Course Management System

Group of four. Each member's deliverables and ownership are listed below. Branches were per-member (`<name>/feature-*`) and merged into `develop`, then `develop` into `main` for the submission.

---

## Camarly Thomas — Lead

**Stream:** Infrastructure, Auth, Caching, Async tasks, Frontend, Bonus features, Postman collection.

- Project scaffolding: `backend/` Flask app factory, `frontend/` Vite + React setup, `nginx/` reverse proxy, `docker-compose.yml` with six services (api, celery_worker, db, redis, frontend, nginx).
- Database layer: 14 numbered SQL migrations in `backend/app/db/migrations/` (auto-run by MySQL on first start), `get_connection()` helper, the 5 SQL views in `014_create_views.sql` that back the report endpoints.
- Authentication: `app/services/auth_service.py` and `app/routes/auth.py` — JWT (PyJWT) issuance + verification, bcrypt password hashing, `register` / `login` / `admin/create-user` endpoints, role enum on the `users` table.
- Middleware: `app/middleware/roles.py` — `@require_role(*roles)` decorator that decodes the bearer token and injects `current_user = {"id": int, "role": str}` as a kwarg.
- Cache: `app/cache/client.py` and `app/cache/keys.py` — Redis client singleton, `cache_get` / `cache_set` / `cache_del` / `cache_del_pattern`, namespaced key builders, TTL constants. Wired into the report endpoints.
- Celery: `app/tasks/celery_app.py`, `grade_tasks.py` (async grade-recalculation), `notification_tasks.py`, `seed_tasks.py`. Redis as broker and result backend.
- Seeding pipeline: `backend/seed/` — 100,000 students, 200 courses, lecturers + admin, enrollments enforcing every spec constraint (3 ≤ courses/student ≤ 6, ≥ 10 members/course, ≤ 5 courses/lecturer, ≥ 1 course/lecturer).
- Frontend: full React (Vite) SPA — auth flow, courses, forums, assignments, grades, calendar, content, reports, role-aware navbar and protected routes.
- Tests: `backend/tests/conftest.py` (in-memory MySQL + Redis fakes so the suite needs no live services), 84-test pytest suite covering every route layer.
- CI/CD: `.github/workflows/ci.yml` (lint + test on PR), `.github/workflows/deploy.yml` (Railway deploy).
- **Postman collection:** `postman/CMS_API.postman_collection.json` — 40 requests across 14 folders, auto-login pre-request script, Local + Railway environment files, README with import + auth-flow walkthrough.
- Forums/threads/replies: assisted Tramonique with the implementation pass.

---

## Carl Heron

**Stream:** Assignments, Submissions, Grades, Reports.

- `app/routes/assignments.py` + `app/services/assignment_service.py` — `POST/GET /api/courses/<id>/assignments`, `GET /api/assignments/<id>`. Date + weight handling, envelope-aligned responses.
- `app/routes/submissions.py` + `app/services/submission_service.py` — `POST /api/assignments/<id>/submit` (student), `GET /api/assignments/<id>/submissions` (lecturer/admin), `GET /api/students/<id>/grades`. Duplicate-submission guard (409).
- `app/routes/grades.py` + `app/services/grade_service.py` — `POST /api/submissions/<id>/grade`. After insert, enqueues the Celery task that recomputes the student's average in `student_averages`.
- `app/routes/reports.py` + `app/services/report_service.py` — all five required reports, each one reading from a SQL view and cached in Redis with a medium TTL:
  - Courses with 50+ students
  - Students enrolled in 5+ courses
  - Lecturers teaching 3+ courses
  - Top 10 most-enrolled courses
  - Top 10 students by average grade

---

## Tamarica Shaw

**Stream:** Courses, Enrollment, Calendar, Content.

- `app/routes/courses.py` + `app/services/course_service.py` — full CRUD plus members, assign-lecturer (enforcing the 5-course cap), per-student and per-lecturer course listings.
- `app/routes/enrollments.py` + `app/services/enrollment_service.py` — `POST /api/courses/<id>/enroll`, enforces the 6-course-per-student cap (403) and duplicate-enrollment guard (409).
- `app/routes/calendar_events.py` + `app/services/calendar_service.py` — create/list course events, plus `GET /api/students/<id>/events?date=YYYY-MM-DD` for the per-day view.
- `app/routes/content.py` + `app/services/content_service.py` — sections + content items with positional ordering, nested in the section listing.

---

## Tramonique Wellington

**Stream:** Forums, Threads, Nested replies (with implementation help from Camarly).

- `app/routes/forums.py` + `app/services/forum_service.py` — `POST/GET /api/courses/<id>/forums`.
- `app/routes/threads.py` + `app/services/thread_service.py` — `POST/GET /api/forums/<id>/threads`, `GET /api/threads/<id>` returns the full nested reply tree.
- `app/routes/replies.py` + `app/services/reply_service.py` — `POST /api/threads/<id>/replies` (top-level) and `POST /api/replies/<id>/replies` (nested at any depth, with parent-existence check).
