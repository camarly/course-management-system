# Course Management System — COMP3161

A full-stack Learning Management System built with Flask, MySQL 8, Redis, Celery, and React.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.x
- [Docker Compose](https://docs.docker.com/compose/) (bundled with Docker Desktop)
- Git

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-org>/course-management-system.git
cd course-management-system
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in every value — see the comments in `.env.example` for guidance.  
**Do not commit your `.env` file.**

### 3. Build and start all services

```bash
docker compose up --build
```

This starts:

| Service | URL |
|---|---|
| React frontend | http://localhost |
| Flask API | http://localhost/api |
| MySQL 8 | localhost:3306 |
| Redis | localhost:6379 (internal) |
| Celery worker | (background worker, no port) |

### 4. Run database migrations

On first start the MySQL container automatically runs every file in  
`backend/app/db/migrations/` in numbered order.

To run them manually against a running container:

```bash
docker compose exec db mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  < backend/app/db/migrations/001_create_users.sql
```

Repeat for each numbered migration file.

### 5. Verify the API is running

```bash
curl http://localhost/api/health
# Expected: {"status": "ok"}
```

---

## Stopping the stack

```bash
docker compose down          # stop containers, keep volumes
docker compose down -v       # stop containers AND delete the MySQL volume
```

---

## Running tests

```bash
docker compose exec api pytest tests/ -v
```

---

## Development workflow

Each team member works on their own feature branch and opens a pull request to `develop`.

```bash
git checkout develop
git pull origin develop
git checkout -b <your-name>/<feature>
```

See the individual setup guides in `docs/` for stream-specific instructions.

---

## Project structure overview

```
course-management-system/
├── backend/        Flask API + Celery worker
├── frontend/       React (Vite) SPA
├── nginx/          Reverse proxy config
├── postman/        API collection and environment
├── docs/           Team guides and architecture docs
└── .github/        CI/CD workflows
```
