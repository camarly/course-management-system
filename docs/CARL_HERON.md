# Ca and rl Heron — Setup & Work Guide

## Your stream
Assignments · Submissions · Grades · Reports

You will ship your first round of work as **three small, incremental pull requests** — one endpoint per PR. Submissions, grading, and the five report endpoints come in later PRs once your first three are merged.

---

## Part A — One-time setup

**Everything runs inside Docker.** You do not need Python, Node, MySQL, or Redis installed on your laptop. The only things on your host are Docker Desktop and Git.

### Step 1. Install the prerequisites
1. Docker Desktop 4.x or newer (confirm the whale icon is running)
2. Git and a terminal

If either fails to install, paste a screenshot in WhatsApp — don't lose an hour to it.

### Step 2. Clone and land on `develop`
1. `git clone git@github.com:camarly/course-management-system.git`
2. `cd course-management-system`
3. `git fetch origin`
4. `git checkout develop`
5. `git pull origin develop`
6. `git status` — should say "nothing to commit, working tree clean"

> **Do not start coding yet.** Wait for Camarly to announce in WhatsApp that Phase 1 is merged to `develop`. Your code depends on `get_connection()`, `@require_role`, and the cache client — none of which exist until Phase 1 is in.

### Step 3. Copy the environment file
1. `cp .env.example .env`
2. That's it. No edits — the defaults are wired for local Docker development.

### Step 4. Bring the stack up
1. `docker compose up --build -d` (3–5 minutes first time)
2. `docker compose ps` — every service must show `running` or `healthy`
3. `curl http://localhost/api/health` → `{"status": "ok", "env": "development"}`

If a service says `exited`, run `docker compose logs <service>` and paste the last 30 lines to the chat.

You're ready to code. All tests and commands run inside the `api` container — you never run `pytest` or `pip` on your host.

---

## Part B — Your first three PRs

Your tests live at `backend/tests/test_assignments.py`. Three classes will turn green in this round. Submissions and grades tests are skipped until your later PRs.

### The three PRs at a glance

| PR | Branch | What you build | Test class it turns green |
|---|---|---|---|
| 1 | `carl/feature-create-assignment` | `POST /api/courses/<id>/assignments` | `TestCreateAssignment` |
| 2 | `carl/feature-list-assignments` | `GET /api/courses/<id>/assignments` | `TestListAssignments` |
| 3 | `carl/feature-get-assignment` | `GET /api/assignments/<id>` | `TestGetAssignment` |

Cut each branch from `develop` **only after the previous PR is merged.** No self-fighting merge conflicts.

---

### PR 1 — `POST /api/courses/<course_id>/assignments`

**Goal:** a lecturer or admin can create an assignment on a course. Students get 403.

#### Step 1. Cut the branch
1. `git checkout develop && git pull origin develop`
2. `git checkout -b carl/feature-create-assignment`

#### Step 2. Read the failing test first
Open `backend/tests/test_assignments.py`. Read `TestCreateAssignment` end to end. Every test gives you:
- The request (method, URL, headers, body)
- The expected response (status, envelope shape)
- Role rules (lecturer + admin allowed, student forbidden)

**The test is the spec.** Don't invent the API — read it.

#### Step 3. Inspect the `assignments` table
1. `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db`
2. `DESCRIBE assignments;`
3. Note NOT NULL columns, types (especially `weight` — it's a DECIMAL), defaults
4. Exit with `\q`

#### Step 4. Create the service file
Create `backend/app/services/assignment_service.py`. This file holds raw SQL only — no Flask.

Write `create_assignment(course_id, title, description, due_date, weight)` so it:
1. Calls `get_connection()` (imported from `app.db.connection`)
2. Wraps in `try:` / `finally: conn.close()`
3. Uses `with conn.cursor() as cur:`
4. Runs `INSERT INTO assignments (...) VALUES (%s, %s, %s, %s, %s)` with a parameter tuple
5. Calls `conn.commit()` — writes without commit vanish
6. Reads `cur.lastrowid`
7. Returns a plain dict the route can jsonify

**Never use f-strings in SQL.** Only `%s`. Breaking this is an automatic bounce.

#### Step 5. Create the route file
Create `backend/app/routes/assignments.py`:
1. `assignments_bp = Blueprint('assignments', __name__, url_prefix='/api')`
2. Define the handler for `POST /courses/<int:course_id>/assignments`
3. Decorate with `@require_role('lecturer', 'admin')`
4. Signature must include BOTH `course_id` (from URL) and `current_user` (from decorator)
5. Parse the body: `request.get_json(silent=True) or {}`
6. Validate required fields: `title`, `due_date`, `weight`. If any are missing, return 400 with `{"error": "missing_fields", "message": "title, due_date, weight required"}`
7. Call the service with the body fields
8. Return `{"data": assignment, "message": "Assignment created"}` with status 201

#### Step 6. Confirm the blueprint is wired
Open `backend/app/__init__.py`. Camarly pre-registered `assignments_bp` in Phase 1. Confirm the import and `register_blueprint` line are there. If missing, add them; otherwise leave alone.

#### Step 7. Run the test
1. `docker compose exec api pytest tests/test_assignments.py::TestCreateAssignment -v`
2. Read every failure. The assertion error tells you exactly what was expected.

> Flask hot-reloads inside the container because `backend/` is mounted as a volume. Save your file, re-run the test — no rebuild needed. Only `requirements.txt` changes need `docker compose build api`.

Common first-round failures:
- **401** — decorator missing or `current_user` missing from the signature
- **403 when 201 expected** — wrong roles in `@require_role`
- **400 always** — your missing-fields check is too strict; `body.get(k) is not None` is the right test so that `0` values pass
- **500** — check `docker compose logs -f api`. Usually a SQL error or forgotten `conn.commit()`
- **`Decimal is not JSON serializable`** — cast `weight` to `float` before returning it from the service

Iterate until green.

#### Step 8. Commit and push
1. `git status` — only your two files
2. `git add backend/app/services/assignment_service.py backend/app/routes/assignments.py`
3. `git commit -m "feat(assignments): POST /api/courses/<id>/assignments"`
4. `git push -u origin carl/feature-create-assignment`

#### Step 9. Open PR 1
On GitHub, open a pull request from `carl/feature-create-assignment` → `develop`.

Description:
- One sentence summary
- Paste the green pytest output for `TestCreateAssignment`
- Anything surprising you ran into

**Do not self-merge.** Wait for Camarly. If changes are requested, push new commits to the same branch.

---

### PR 2 — `GET /api/courses/<course_id>/assignments`

#### Step 1. Sync and cut the new branch
1. `git checkout develop`
2. `git pull origin develop` (pulls your merged PR 1)
3. `git checkout -b carl/feature-list-assignments`

#### Step 2. Read `TestListAssignments`
Note any expected ordering (likely by `due_date`). Match it in your SQL.

#### Step 3. Add `list_for_course(course_id)` to the service
1. Same try/finally/cursor structure
2. `SELECT id, course_id, title, description, due_date, weight, created_at FROM assignments WHERE course_id = %s ORDER BY due_date`
3. Return `cur.fetchall()`
4. No `commit` (read)

#### Step 4. Add the GET route
1. `GET /courses/<int:course_id>/assignments`
2. `@require_role('admin', 'lecturer', 'student')` — any logged-in user
3. Signature: `course_id`, `current_user`
4. Return `{"data": assignments, "message": None}`, 200

#### Step 5. Run the test, commit, push, PR
Same flow as PR 1. Branch is `carl/feature-list-assignments`.

---

### PR 3 — `GET /api/assignments/<assignment_id>`

#### Step 1. Sync and cut the branch
1. `git checkout develop && git pull origin develop`
2. `git checkout -b carl/feature-get-assignment`

#### Step 2. Read `TestGetAssignment`
Note the two cases: 404 when missing, 200 when found. Both must pass.

#### Step 3. Add `get_assignment(assignment_id)` to the service
Return either a dict or `None`. Use `cur.fetchone()` — it returns `None` when there are no rows.

#### Step 4. Add the route
Path: `/assignments/<int:assignment_id>` (note: top-level `/api/assignments`, not under `/courses`). Return a 404 envelope when the service returns `None`.

#### Step 5. Run the tests, commit, push, PR
Same flow.

When PR 3 is merged, `TestCreateAssignment`, `TestListAssignments`, and `TestGetAssignment` are all green on `develop`.

---

## Part C — Later PRs (after your first three merge)

### Submissions & grading
| PR | Branch | Endpoint |
|---|---|---|
| Submit an assignment | `carl/feature-submit-assignment` | `POST /api/assignments/<id>/submit` (student) |
| List submissions | `carl/feature-list-submissions` | `GET /api/assignments/<id>/submissions` (lecturer, admin) |
| Grade a submission | `carl/feature-grade-submission` | `POST /api/submissions/<id>/grade` (lecturer) |
| Student's grades | `carl/feature-student-grades` | `GET /api/students/<id>/grades` (student/own, admin) |

For grading, compute the student average **synchronously** inside the service for now (plain `AVG(...)` SQL). Camarly will swap this for an async Celery task in Phase 3 — you don't need to touch Celery.

### Reports (Phase 3)
All five reports are backed by SQL views from migration `014_create_views.sql`. Each endpoint is a single `SELECT * FROM <view>`. All five are admin-only and all five will be cached — Camarly will add cache calls on review.

| PR branch | Endpoint | Source view |
|---|---|---|
| `carl/feature-report-courses-50-plus` | `GET /api/reports/courses-50-plus` | `vw_courses_50_plus` |
| `carl/feature-report-students-5-plus` | `GET /api/reports/students-5-plus-courses` | `vw_students_5_plus_courses` |
| `carl/feature-report-lecturers-3-plus` | `GET /api/reports/lecturers-3-plus-courses` | `vw_lecturers_3_plus_courses` |
| `carl/feature-report-top10-courses` | `GET /api/reports/top10-enrolled-courses` | `vw_top10_enrolled_courses` |
| `carl/feature-report-top10-students` | `GET /api/reports/top10-students-by-average` | `vw_top10_students_by_average` |

---

## Part D — The six non-negotiable rules

Every PR must pass all six:

1. **Every service function opens `get_connection()` and closes it in `finally`.**
2. **`%s` placeholders only.** No f-strings, no `.format()`, no concatenation in SQL.
3. **Every protected route has `@require_role(...)` and `current_user` in its signature.**
4. **Every write calls `conn.commit()` before returning.**
5. **Every response uses the envelope**: `{"data": ..., "message": ...}` or `{"error": "code", "message": "text"}`.
6. **Never return `password_hash`** in any SELECT touching `users`.

---

## Part E — Everyday Docker commands

| What you want | Command |
|---|---|
| Start everything | `docker compose up -d` |
| Start only MySQL + Redis | `docker compose up -d db redis` |
| Tail API logs | `docker compose logs -f api` |
| Tail Celery logs | `docker compose logs -f celery_worker` |
| Restart API after code change | `docker compose restart api` |
| MySQL shell | `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db` |
| Redis shell | `docker compose exec redis redis-cli` |
| Stop, keep data | `docker compose down` |
| Nuke DB volume | `docker compose down -v` |
| Run tests in container | `docker compose exec api pytest tests/test_assignments.py -v` |

---

## Part F — Frontend input
Bring to the next meeting:
- Grade table colour scheme (row colours, badge colours for A/B/C/F)
- Report page table styles and chart palette

---

## Part G — Stuck? Read this before messaging

| Symptom | Fix |
|---|---|
| `docker compose up` port in use | `lsof -i :80`; kill the offender or change the port |
| `pytest: command not found` on your host | You're running pytest outside Docker — use `docker compose exec api pytest ...` |
| `ModuleNotFoundError: No module named 'app'` | Same cause — run pytest inside the container with `docker compose exec api pytest ...` |
| Tests 404 on your routes | URL rule doesn't match — compare char by char with the test's path |
| Tests 401 everywhere | Likely a conftest import issue — paste the full trace |
| `OperationalError: (2003)` | MySQL not up — `docker compose up -d db`, wait 10s, retry |
| `cur.execute` "not enough arguments" | Missing trailing comma in tuple: `(x,)` not `(x)` |
| `Decimal is not JSON serializable` | Cast `float(weight)` in the service before returning |

**When messaging for help, include:**
1. The exact command you ran
2. The exact output (copy-paste, not paraphrase)
3. What you expected

If you're stuck for more than 30 minutes, ping the chat. Camarly would rather unblock you in 2 minutes than see you spin for an hour.
