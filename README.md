# Course Management System — COMP3161

A full-stack Learning Management System built with Flask, MySQL 8, Redis, Celery, and React.

Everything runs inside Docker. You do not need Python, Node, MySQL, or Redis installed locally — only Docker Desktop and Git.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.x or newer (includes Docker Compose)
- Git

---

## Quick Start

### 1. Clone the repository

```bash
git clone git@github.com:camarly/course-management-system.git
cd course-management-system
```

### 2. Copy the environment file

```bash
cp .env.example .env
```

No edits required — the defaults are wired for local development inside Docker.

### 3. Bring the stack up

```bash
docker compose up --build -d
```

This starts six services:

| Service | URL / Port |
|---|---|
| React frontend | http://localhost:5173 |
| Flask API (via nginx) | http://localhost/api |
| MySQL 8 | localhost:3306 |
| Redis | internal only (6379) |
| Celery worker | background, no port |
| nginx reverse proxy | http://localhost |

On **first start**, MySQL automatically runs every `.sql` file in `backend/app/db/migrations/` — no manual migration step is needed.

### 4. Verify the API

```bash
curl http://localhost/api/health
# → {"status": "ok", "env": "development"}
```

---

## Running tests

All tests run **inside the API container** — no Python venv, no `pip install`, nothing on your host:

```bash
docker compose exec api pytest tests/ -v
```

Run a specific file or class:

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

## Authentication (JWT)

The API uses JWT — no Google OAuth. See `docs/PROJECT_PLAN.md` for the full auth flow.

```bash
# Register
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "secret123", "role": "student"}'

# Login — returns a JWT
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "secret123"}'

# Call a protected route
curl http://localhost/api/users/me -H "Authorization: Bearer <token>"
```

---

## Development workflow

Each team member works on a small, incremental feature branch and opens a pull request to `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b <your-name>/feature-<what-you-are-building>
```

See `docs/TAMARICA_SHAW.md`, `docs/TRAMONIQUE_WELLINGTON.md`, and `docs/CARL_HERON.md` for each stream's step-by-step guide.

---

## Project structure

```
course-management-system/
├── backend/        Flask API + Celery worker
├── frontend/       React (Vite) SPA
├── nginx/          Reverse proxy config
├── postman/        API environment template
├── docs/           Team guides and architecture docs
└── .github/        CI workflows
```
