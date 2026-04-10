# Course Management System — COMP3161

A full-stack Learning Management System built with Flask, MySQL 8, Redis, Celery, and React.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) >= 4.x (includes Docker Compose)
- Git

---

## Quick Start

### 1. Clone the repository

```bash
git clone <repo-url>
cd course-management-system
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in every value — see the comments in `.env.example` for guidance.

Required secrets to generate:

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# JWT_SECRET (use a different value from SECRET_KEY)
python -c "import secrets; print(secrets.token_hex(32))"
```

**Do not commit your `.env` file.**

### 3. Build and start all services

```bash
docker compose up --build
```

This starts:

| Service | URL / Port |
|---|---|
| React frontend | http://localhost:5173 |
| Flask API (via nginx) | http://localhost/api |
| MySQL 8 | localhost:3306 |
| Redis | internal only (6379) |
| Celery worker | background, no port |

### 4. Database migrations

On **first start**, MySQL automatically runs every `.sql` file in `backend/app/db/migrations/` (mounted to `/docker-entrypoint-initdb.d`). This only happens when the `mysql_data` volume is empty.

To re-run migrations on an existing database (e.g. after adding a new migration):

```bash
docker compose exec -T db mysql -u"$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" \
  < backend/app/db/migrations/<filename>.sql
```

To re-run all migrations from scratch:

```bash
docker compose down -v        # deletes the MySQL volume
docker compose up --build -d  # recreates everything
```

### 5. Verify the API is running

```bash
curl http://localhost/api/health
# Expected: {"status": "ok"}
```

---

## Authentication (JWT)

The API uses JSON Web Tokens for authentication. See `docs/CAMARLY_THOMAS.md` for full JWT setup and usage instructions.

Quick reference:

```bash
# Register
curl -X POST http://localhost/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "secret123", "role": "student"}'

# Login — returns a JWT in the response
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "secret123"}'

# Use the token on protected routes
curl http://localhost/api/users/me \
  -H "Authorization: Bearer <token>"
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

## Project structure

```
course-management-system/
├── backend/        Flask API + Celery worker
├── frontend/       React (Vite) SPA
├── nginx/          Reverse proxy config
├── postman/        API environment template (collection exported from Postman)
├── docs/           Team guides and architecture docs
└── .github/        CI/CD workflows
```
