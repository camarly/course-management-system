# Tamarica Shaw — Setup & Work Guide

## Your stream
Courses · Enrollment · Calendar Events · Course Content · Postman Collection

You will ship your first PR as **three small, incremental pull requests** — one endpoint per PR. Each PR unblocks the next. This is on purpose: small PRs are easier to review, easier to fix, and teach you the review loop.

---

## Part A — One-time setup

**Everything runs inside Docker.** You do not need Python, Node, MySQL, or Redis installed on your laptop. The only things on your host machine are Docker Desktop and Git.

### Step 1. Install the prerequisites
1. Docker Desktop 4.x or newer (make sure the whale icon in your menu bar is running)
2. Git and a terminal you're comfortable in

If either install fails, message Camarly in WhatsApp with a screenshot — don't burn an hour fighting it.

### Step 2. Clone the repo and land on `develop`
Run these one by one. Read the output of each before running the next.

1. `git clone git@github.com:camarly/course-management-system.git`
2. `cd course-management-system`
3. `git fetch origin`
4. `git checkout develop`
5. `git pull origin develop`
6. `git status` — should say "nothing to commit, working tree clean"

> **Do not start coding yet.** Wait for Camarly to announce in WhatsApp that Phase 1 is on `develop`. Until then, the shared infrastructure your code depends on (DB connection, `@require_role`, cache client) is not in place.

### Step 3. Copy the environment file
1. `cp .env.example .env`
2. That's it. No edits — the defaults are wired for local development inside Docker.

### Step 4. Bring the Docker stack up
1. `docker compose up --build -d`
   Builds the Flask image, pulls MySQL and Redis, starts all six services. Expect 3–5 minutes the first time.
2. `docker compose ps`
   Every service should show `running` or `healthy`. If any say `exited`, run `docker compose logs <service>` and paste the last 30 lines to the chat.
3. `curl http://localhost/api/health`
   You should see `{"status": "ok", "env": "development"}`. If you don't, the API container isn't ready yet — wait 15 seconds and try again.

You're ready to code. All tests and commands run inside the `api` container — you never run `pytest` or `pip` on your host.

---

## Part B — Your first PR (broken into 3 incremental PRs)

Your tests live at `backend/tests/test_courses.py`. They're already written and currently red. Your job is to turn them green one class at a time, opening a separate pull request after each one.

### The three PRs at a glance

| PR | Branch | What you build | Test class it turns green |
|---|---|---|---|
| 1 | `tamarica/feature-create-course` | `POST /api/courses` | `TestCreateCourse` |
| 2 | `tamarica/feature-list-courses` | `GET /api/courses` | `TestListCourses` |
| 3 | `tamarica/feature-get-course` | `GET /api/courses/<id>` | `TestGetCourse` |

Cut each branch from `develop` **only after the previous PR is merged.** That way you never fight merge conflicts with yourself.

---

### PR 1 — `POST /api/courses` (create a course)

**Goal:** an admin can create a course. Students and lecturers get 403.

#### Step 1. Cut the branch
1. Make sure you're on `develop` and fully up to date: `git checkout develop && git pull origin develop`
2. Create your branch: `git checkout -b tamarica/feature-create-course`

#### Step 2. Read the failing test first
Open `backend/tests/test_courses.py` and read the `TestCreateCourse` class. Every test tells you three things:
- What request to make (method, URL, headers, body)
- What response is expected (status code, envelope shape)
- What role restrictions apply

**Read the test before writing code.** The test is the spec.

#### Step 3. Explore the schema
You need to know what columns `courses` has before writing the INSERT.

1. `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db`
2. `DESCRIBE courses;`
3. Note the column names, which are NOT NULL, and which have defaults.
4. Exit with `\q`.

#### Step 4. Create the service file
Create `backend/app/services/course_service.py`. This file holds the database logic — no Flask, no routing, just a function that takes arguments and talks to MySQL.

Write a function `create_course(title, description, lecturer_id)` that:
1. Opens a connection with `get_connection()` (imported from `app.db.connection`)
2. Wraps everything in `try:` / `finally: conn.close()`
3. Opens a cursor with `with conn.cursor() as cur:`
4. Runs an `INSERT INTO courses (...) VALUES (%s, %s, %s)` using a parameter tuple — **never** an f-string
5. Calls `conn.commit()` (writes without commit vanish)
6. Reads `cur.lastrowid` to get the new ID
7. Returns a plain dict with the fields (so the route can jsonify it)

Rule of thumb: if you ever find yourself typing a `{variable}` inside a SQL string, stop — use `%s` and add to the tuple.

#### Step 5. Create the route file
Create `backend/app/routes/courses.py`. This is the thin Flask layer that receives HTTP requests, validates them, and calls your service.

1. Create a Blueprint called `courses_bp` with `url_prefix='/api'`
2. Define a function for `POST /courses` decorated with `@courses_bp.route(...)` and `@require_role('admin')`
3. The function signature MUST include `current_user` as a keyword argument — the decorator injects it
4. Parse the JSON body with `request.get_json(silent=True) or {}`
5. Return a 400 with `{"error": "missing_fields", "message": ...}` if `title` is missing
6. Call `course_service.create_course(...)` with the body fields
7. Return `jsonify({"data": course, "message": "Course created"}), 201`

#### Step 6. Wire the blueprint into the app
Open `backend/app/__init__.py`. The `register_blueprints` function should already import and register your blueprint — Camarly pre-wired it in Phase 1. Verify the line is there. If it's missing, add it; if it's present, leave it alone.

#### Step 7. Run the test
1. `docker compose exec api pytest tests/test_courses.py::TestCreateCourse -v`
2. Read each failure message carefully. The error tells you what the test expected and what it got.

> Flask hot-reloads inside the container because the `backend/` folder is mounted as a volume. Save your file, re-run the test — no rebuild needed. If you edit `requirements.txt`, that's the one case you need `docker compose build api` + `docker compose up -d api`.

Common first-round failures:
- **401 where the test expected 201** — you forgot `current_user` in the signature, or the test isn't sending a token (it is — check your decorator)
- **`KeyError: 'title'`** — the test sent an empty body; you didn't check for missing fields
- **`TypeError: not enough arguments for format string`** — your parameter tuple has the wrong number of `%s` placeholders
- **`InternalError: (0, '')`** — you forgot `conn.commit()`

Iterate until all three tests in `TestCreateCourse` pass.

#### Step 8. Commit and push
1. `git status` — only your two files should be listed
2. `git add backend/app/services/course_service.py backend/app/routes/courses.py`
3. `git commit -m "feat(courses): POST /api/courses endpoint"`
4. `git push -u origin tamarica/feature-create-course`

#### Step 9. Open the PR
Go to GitHub, open a pull request from `tamarica/feature-create-course` → `develop`.

In the PR description, include:
- One sentence summary: *"Adds POST /api/courses for admin course creation."*
- Paste the green pytest output for `TestCreateCourse`
- Anything surprising you learned (Camarly uses this for mentoring)

**Do not self-merge.** Wait for Camarly's review. If changes are requested, push new commits to the same branch — don't open a new PR.

Once merged, PR 2 is unblocked.

---

### PR 2 — `GET /api/courses` (list all courses)

#### Step 1. Sync and cut the new branch
1. `git checkout develop`
2. `git pull origin develop` (this now includes your merged PR 1 code)
3. `git checkout -b tamarica/feature-list-courses`

#### Step 2. Read the `TestListCourses` test class
Same rule: read the spec before writing code.

#### Step 3. Add `list_courses()` to your service file
Add a function that:
1. Takes no arguments
2. Opens a connection, wraps in try/finally
3. Runs `SELECT id, title, description, lecturer_id, created_at FROM courses ORDER BY id`
4. Returns `cur.fetchall()` — this is a list of dicts because we use `DictCursor`

No commit needed — this is a read.

#### Step 4. Add the route
Add `GET /courses` to `backend/app/routes/courses.py`:
1. Decorate with `@require_role('admin', 'lecturer', 'student')` (any logged-in user)
2. Include `current_user` in the signature even though you don't use it
3. Call the service and return `jsonify({"data": courses, "message": None}), 200`

#### Step 5. Run the test
`docker compose exec api pytest tests/test_courses.py::TestListCourses -v`

#### Step 6. Commit, push, and open PR 2
Same flow as PR 1, but the branch is `tamarica/feature-list-courses`. Wait for merge.

---

### PR 3 — `GET /api/courses/<id>` (get one course)

#### Step 1. Sync and cut the branch
1. `git checkout develop && git pull origin develop`
2. `git checkout -b tamarica/feature-get-course`

#### Step 2. Read `TestGetCourse`
Note that it has two tests: 404 when missing, 200 when found. You must handle both.

#### Step 3. Add `get_course(course_id)` to the service
Returns either a dict (when the row exists) or `None` (when it doesn't). Use `cur.fetchone()` — it returns `None` automatically when there are no rows.

#### Step 4. Add the route
Path: `/courses/<int:course_id>` — the `int:` converter means Flask rejects non-numeric IDs for you. Return 404 with the error envelope when the service returns `None`.

#### Step 5. Run the tests, commit, push, PR
Same flow.

When PR 3 is merged, your first round of work is complete and `TestCreateCourse`, `TestListCourses`, `TestGetCourse` are all green on `develop`.

---

## Part C — After your first three PRs are merged

More branches open up. Each is still one small PR per feature:

| Future PR | Branch name pattern |
|---|---|
| Enroll a student | `tamarica/feature-enroll-student` |
| List course members | `tamarica/feature-course-members` |
| Assign lecturer (one per course, cap 5) | `tamarica/feature-assign-lecturer` |
| Student's courses | `tamarica/feature-student-courses` |
| Lecturer's courses | `tamarica/feature-lecturer-courses` |
| Create calendar event | `tamarica/feature-create-event` |
| List calendar events | `tamarica/feature-list-events` |
| Student events by date | `tamarica/feature-student-events` |
| Create section / content item | `tamarica/feature-course-content` |

Business rules you must enforce in later PRs (Camarly will remind you in reviews):
- A student cannot enroll in more than **6** courses → return 403
- A lecturer cannot be assigned more than **5** courses → return 403
- A course has **one** lecturer at a time → replace, don't append
- Duplicate enrollment → 409

---

## Part D — The six non-negotiable rules

Every PR you open must pass all six. Camarly will bounce PRs that break any of them.

1. **Every service function opens `get_connection()` and closes it in a `finally` block.** No exceptions.
2. **Always `%s` placeholders with a parameter tuple.** Never f-strings, never `.format()`, never string concatenation. SQL injection is an automatic bounce.
3. **Every protected route has `@require_role(...)` and `current_user` in its signature.**
4. **Every write calls `conn.commit()` before returning.** Writes without commit silently vanish.
5. **Every response uses the envelope**: success is `{"data": ..., "message": ...}`, failure is `{"error": "code", "message": "human text"}`.
6. **Never return `password_hash`** in any SELECT that touches the `users` table.

---

## Part E — Everyday Docker commands

| What you want | Command |
|---|---|
| Start everything in the background | `docker compose up -d` |
| Start only MySQL + Redis (lighter) | `docker compose up -d db redis` |
| Tail Flask logs live | `docker compose logs -f api` |
| Restart Flask after a code change | `docker compose restart api` |
| Open a MySQL shell | `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db` |
| Open a Redis shell | `docker compose exec redis redis-cli` |
| Stop the stack (keep DB data) | `docker compose down` |
| Nuke the DB volume | `docker compose down -v` |
| Run your tests inside the API container | `docker compose exec api pytest tests/test_courses.py -v` |

---

## Part F — Postman folders you own
- Courses
- Enrollment
- Calendar Events
- Content
- Assignments
- Submissions

You share the environment file with Tramonique. Coordinate on variable names (`base_url`, `jwt_admin`, `jwt_student`, `course_id`).

---

## Part G — Frontend input
Bring to the next meeting:
- Course card layout + colour palette
- Calendar event badge colours
- Enrollment status indicators (enrolled vs. available)

---

## Part H — Stuck? Read this before messaging

| Symptom | Fix |
|---|---|
| `docker compose up` fails with "port already in use" | `lsof -i :80`; kill the offender or change the port |
| `pytest: command not found` on your host | You're running pytest outside Docker — use `docker compose exec api pytest ...` instead |
| `ModuleNotFoundError: No module named 'app'` | You're running pytest on your host — use `docker compose exec api pytest ...` |
| Tests 404 on your routes | URL rule doesn't match the test's path — compare them character by character |
| Tests 401 everywhere | Stack trace likely shows a conftest import issue — paste it to the chat |
| `OperationalError: (2003)` | MySQL isn't up yet — `docker compose up -d db`, wait 10s, retry |
| `cur.execute` crashes with "not enough arguments" | Missing trailing comma: `(x,)` not `(x)` |

**When you message the group for help, include:**
1. The exact command you ran
2. The exact output (copy-paste, not paraphrase)
3. What you expected to happen

If you're stuck for more than 30 minutes, message the chat. Camarly would rather unblock you in 2 minutes than have you spin for an hour.
