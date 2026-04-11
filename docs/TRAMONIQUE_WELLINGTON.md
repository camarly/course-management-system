# Tramonique Wellington — Setup & Work Guide

## Your stream
Forums · Threads · Nested Replies · Postman Collection

You will ship your first round of work as **two small, incremental pull requests** — one endpoint per PR. Threads and the nested reply tree come in later PRs once your first two are merged.

---

## Part A — One-time setup

**Everything runs inside Docker.** You do not need Python, Node, MySQL, or Redis installed on your laptop. The only things on your host are Docker Desktop and Git.

### Step 1. Install the prerequisites
1. Docker Desktop 4.x or newer (check the whale icon is running)
2. Git and a terminal

If either fails to install, paste a screenshot in WhatsApp — don't fight it for an hour.

### Step 2. Clone and land on `develop`
1. `git clone git@github.com:camarly/course-management-system.git`
2. `cd course-management-system`
3. `git fetch origin`
4. `git checkout develop`
5. `git pull origin develop`
6. `git status` — should say "nothing to commit, working tree clean"

> **Do not start coding yet.** Wait for Camarly's WhatsApp announcement that Phase 1 is on `develop`. Your code imports `get_connection`, `require_role`, and the cache client — until those land, nothing will run.

### Step 3. Copy the environment file
1. `cp .env.example .env`
2. That's it. No edits — the defaults are wired for local Docker development.

### Step 4. Bring the stack up
1. `docker compose up --build -d` (3–5 minutes the first time)
2. `docker compose ps` — every service must be `running` or `healthy`
3. `curl http://localhost/api/health` should return `{"status": "ok", "env": "development"}`

If a service shows `exited`, run `docker compose logs <service>` and paste the last 30 lines to the chat.

You're ready to code. All tests and commands run inside the `api` container — you never run `pytest` or `pip` on your host.

---

## Part B — Your first two PRs

Your tests live at `backend/tests/test_forums.py`. Two classes will turn green in this first round. Thread and reply tests are skipped until your later PRs.

### The two PRs at a glance

| PR | Branch | What you build | Test class it turns green |
|---|---|---|---|
| 1 | `tramonique/feature-create-forum` | `POST /api/courses/<id>/forums` | `TestCreateForum` |
| 2 | `tramonique/feature-list-forums` | `GET /api/courses/<id>/forums` | `TestListForums` |

Cut PR 2's branch from `develop` **only after PR 1 is merged.**

---

### PR 1 — `POST /api/courses/<course_id>/forums`

#### Step 1. Cut the branch
1. `git checkout develop && git pull origin develop`
2. `git checkout -b tramonique/feature-create-forum`

#### Step 2. Read the failing test first
Open `backend/tests/test_forums.py`. Read the `TestCreateForum` class end to end. Every test tells you:
- The request (method, URL, headers, body)
- The expected response (status code, envelope shape)
- Which roles are allowed (lecturer + admin) and which are not (student = 403)

**The test is the spec.** Never guess at the API — read it.

#### Step 3. Inspect the `forums` table
1. `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db`
2. `DESCRIBE forums;`
3. Note which columns are NOT NULL and which have defaults.
4. Exit with `\q`.

#### Step 4. Create the service file
Create `backend/app/services/forum_service.py`. This file holds raw SQL only — no Flask.

Write `create_forum(course_id, title, description, created_by)` so it:
1. Calls `get_connection()` (imported from `app.db.connection`)
2. Wraps the body in `try:` / `finally: conn.close()`
3. Uses `with conn.cursor() as cur:`
4. Runs an `INSERT INTO forums (...) VALUES (%s, %s, %s, %s)` with a parameter tuple
5. Calls `conn.commit()` — writes without commit vanish silently
6. Reads `cur.lastrowid` for the new ID
7. Returns a plain dict the route can jsonify

**Never use f-strings or `.format()` inside a SQL string.** Only `%s` placeholders. This is non-negotiable.

#### Step 5. Create the route file
Create `backend/app/routes/forums.py`:
1. Create `forums_bp = Blueprint('forums', __name__, url_prefix='/api')`
2. Define a function for `POST /courses/<int:course_id>/forums`
3. Decorate with `@require_role('lecturer', 'admin')`
4. The function signature MUST include both `course_id` (from the URL) and `current_user` (injected by the decorator)
5. Parse the body: `request.get_json(silent=True) or {}`
6. If `title` is missing, return `{"error": "missing_fields", "message": "title required"}` with status 400
7. Call the service. Pass `created_by=current_user['id']` so the DB knows who created the forum
8. Return `{"data": forum, "message": "Forum created"}` with status 201

#### Step 6. Confirm the blueprint is wired
Open `backend/app/__init__.py`. Camarly already registered `forums_bp` in Phase 1 — confirm the import and `register_blueprint` line are present. If missing, add them; otherwise leave alone.

#### Step 7. Run the test
1. `docker compose exec api pytest tests/test_forums.py::TestCreateForum -v`
2. Read each failure. The assertion tells you exactly what was expected vs. what happened.

> Flask hot-reloads inside the container because `backend/` is mounted as a volume. Save your file, re-run the test — no rebuild needed. Only `requirements.txt` changes need `docker compose build api`.

Common first-round failures:
- **401** — your decorator is missing or `current_user` isn't in the signature
- **403 where the test expected 201** — you used the wrong roles in `@require_role`
- **400** — your missing-field check is firing when it shouldn't; print the body
- **500** — check the API logs: `docker compose logs -f api`. Usually a SQL error or forgotten `conn.commit()`

Iterate until green.

#### Step 8. Commit and push
1. `git status` — only your two files
2. `git add backend/app/services/forum_service.py backend/app/routes/forums.py`
3. `git commit -m "feat(forums): POST /api/courses/<id>/forums"`
4. `git push -u origin tramonique/feature-create-forum`

#### Step 9. Open PR 1
On GitHub, open a PR from `tramonique/feature-create-forum` → `develop`.

In the description:
- One sentence summary
- Paste the green pytest output for `TestCreateForum`
- Anything surprising you ran into

**Do not self-merge.** Wait for Camarly. If they request changes, push new commits to the same branch.

---

### PR 2 — `GET /api/courses/<course_id>/forums`

#### Step 1. Sync and cut the new branch
1. `git checkout develop`
2. `git pull origin develop` (pulls your merged PR 1)
3. `git checkout -b tramonique/feature-list-forums`

#### Step 2. Read `TestListForums`
Note the expected ordering — the test likely checks newest first. Your ORDER BY must match.

#### Step 3. Add `list_forums(course_id)` to the service file
1. Same try/finally/cursor structure
2. `SELECT id, course_id, title, description, created_by, created_at FROM forums WHERE course_id = %s ORDER BY created_at DESC`
3. Return `cur.fetchall()` — this is a list of dicts
4. No `commit` needed (this is a read)

#### Step 4. Add the GET route
1. `GET /courses/<int:course_id>/forums`
2. Decorate with `@require_role('admin', 'lecturer', 'student')` — any logged-in user
3. Include both `course_id` and `current_user` in the signature
4. Return `{"data": forums, "message": None}` with status 200

#### Step 5. Run the test, commit, push, PR
Same flow as PR 1. Branch is `tramonique/feature-list-forums`.

When PR 2 is merged, `TestCreateForum` and `TestListForums` are both green on `develop`, and your first round is done.

---

## Part C — Later PRs (after your first two merge)

### PR 3 — Create a thread in a forum
Branch: `tramonique/feature-create-thread`
Endpoint: `POST /api/forums/<forum_id>/threads` (any logged-in user)

### PR 4 — List threads in a forum
Branch: `tramonique/feature-list-threads`
Endpoint: `GET /api/forums/<forum_id>/threads`

### PR 5 — Get a thread with its full nested reply tree
Branch: `tramonique/feature-get-thread`
Endpoint: `GET /api/threads/<thread_id>`

### PR 6 — Reply directly to a thread
Branch: `tramonique/feature-reply-to-thread`
Endpoint: `POST /api/threads/<thread_id>/replies`

### PR 7 — Reply to a reply (nested)
Branch: `tramonique/feature-reply-to-reply`
Endpoint: `POST /api/replies/<reply_id>/replies`

### The nested reply pattern — read this before PR 5
The `replies` table has a self-referencing foreign key `parent_reply_id`:
- `NULL` means "direct reply to the thread"
- A non-NULL value means "reply to another reply"

To fetch the whole reply tree for a thread in one query, you will use a **MySQL 8 recursive CTE**. The shape:
1. Seed clause: select direct replies to the thread (parent is NULL)
2. Recursive clause: join `replies` to the working set on `parent_reply_id`
3. UNION ALL the two

Then in Python, you walk the flat rows once and assemble them into a nested tree by grouping children under their parent ID.

This is the one genuinely tricky part of your stream. **When you get to PR 5, message Camarly and pair on the CTE** — this is exactly the kind of thing we pair on, not the kind of thing you should burn 2 hours on alone.

---

## Part D — The six non-negotiable rules

Every PR must pass all six:

1. **Every service function opens `get_connection()` and closes it in `finally`.**
2. **`%s` placeholders only.** No f-strings, no `.format()`, no concatenation in SQL.
3. **Every protected route has `@require_role(...)` and `current_user` in its signature.**
4. **Every write calls `conn.commit()` before returning.**
5. **Every response uses the envelope**: `{"data": ..., "message": ...}` or `{"error": "code", "message": "text"}`.
6. **Never return `password_hash`** in any SELECT that touches `users`.

---

## Part E — Everyday Docker commands

| What you want | Command |
|---|---|
| Start everything | `docker compose up -d` |
| Start only MySQL + Redis | `docker compose up -d db redis` |
| Tail API logs | `docker compose logs -f api` |
| Restart API after code change | `docker compose restart api` |
| MySQL shell | `docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" lms_db` |
| Redis shell | `docker compose exec redis redis-cli` |
| Stop, keep data | `docker compose down` |
| Nuke DB volume | `docker compose down -v` |
| Run tests inside container | `docker compose exec api pytest tests/test_forums.py -v` |

---

## Part F — Postman folders you own
- Auth
- Forums
- Threads
- Replies
- Grades
- Reports

Share the environment file with Tamarica. Agree on variable names up front (`base_url`, `jwt_admin`, `jwt_student`, `forum_id`, `thread_id`).

---

## Part G — Frontend input
Bring to the next meeting:
- Forum list and thread card design
- Reply indentation style (colour per depth level)
- Accent colour for the discussion section

---

## Part H — Stuck? Read this before messaging

| Symptom | Fix |
|---|---|
| `docker compose up` port in use | `lsof -i :80`; kill the offender or change the port |
| `pytest: command not found` on your host | You're running pytest outside Docker — use `docker compose exec api pytest ...` |
| `ModuleNotFoundError: No module named 'app'` | Same cause — run pytest inside the container with `docker compose exec api pytest ...` |
| Tests 404 on `/api/courses/1/forums` | Your route path doesn't match the blueprint URL rule — compare char by char |
| Tests 401 everywhere | Usually a conftest import failure — paste the full trace |
| `OperationalError: (2003)` | MySQL not up — `docker compose up -d db`, wait 10s, retry |
| Recursive CTE returns wrong rows | Seed clause must filter both `thread_id` AND `parent_reply_id IS NULL` |

**When messaging for help, include:**
1. The exact command you ran
2. The exact output (copy-paste, don't paraphrase)
3. What you expected

If you're stuck for more than 30 minutes, ping the chat. Camarly would rather unblock you in 2 minutes than see you spin for an hour.
