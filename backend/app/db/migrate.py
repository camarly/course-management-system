"""
Idempotent migration runner.

Reads every *.sql file in app/db/migrations/ in lexicographic order
and executes each statement against the configured database. All
migrations use CREATE TABLE IF NOT EXISTS / CREATE OR REPLACE VIEW,
so re-running on every startup is safe.

Used by:
    - create_app() at startup (Railway has no docker-entrypoint-initdb.d
      hook, so the schema must be applied by the application itself).
    - `python -m app.db.migrate` for manual one-off invocations.
"""

import logging
from pathlib import Path

from app.db.connection import get_connection

logger = logging.getLogger(__name__)

_MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"


def _split_statements(sql: str):
    """
    Split a SQL file into individual statements on `;`.

    Handles -- line comments and blank lines. Our migration files
    don't use stored procedures, triggers, or DELIMITER blocks, so a
    naive split is sufficient.
    """
    cleaned_lines = []
    for line in sql.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def run_migrations():
    """Apply every migration file in order. Safe to call repeatedly."""
    files = sorted(_MIGRATIONS_DIR.glob("*.sql"))
    if not files:
        logger.warning("No migration files found in %s", _MIGRATIONS_DIR)
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for path in files:
                logger.info("Applying migration: %s", path.name)
                statements = _split_statements(path.read_text())
                for stmt in statements:
                    cur.execute(stmt)
        conn.commit()
        logger.info("Migrations applied: %d file(s)", len(files))
    finally:
        conn.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    run_migrations()
