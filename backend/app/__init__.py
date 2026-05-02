"""
Flask application factory.

create_app() initialises the Flask app, loads configuration,
registers CORS, and mounts all route blueprints.
"""

import logging
import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from app import config

# Path inside the combined image (built by the root Dockerfile) where
# the React production build is copied. When this directory exists at
# runtime, Flask serves the SPA at "/" and falls back to index.html for
# unknown non-API paths so client-side routes like /courses/123 work
# on a hard refresh. When it doesn't exist (local docker-compose, where
# nginx + Vite handle the frontend), the SPA route is simply not
# registered — the API runs exactly as before.
_FRONTEND_DIR = os.environ.get("FRONTEND_STATIC_DIR", "/app/static_frontend")

logger = logging.getLogger(__name__)


def create_app():
    """Build and return the configured Flask application."""
    app = Flask(__name__)

    # --- Config -----------------------------------------------------------
    app.config["SECRET_KEY"] = config.SECRET_KEY
    app.config["ENV"] = config.FLASK_ENV
    app.config["DEBUG"] = config.FLASK_DEBUG

    # --- CORS (allows React dev server on port 5173) ----------------------
    CORS(app)

    # --- Logging ----------------------------------------------------------
    logging.basicConfig(
        level=logging.DEBUG if config.FLASK_DEBUG else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # --- Blueprints -------------------------------------------------------
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.courses import courses_bp
    from app.routes.enrollments import enrollments_bp
    from app.routes.calendar_events import calendar_bp as calendar_events_bp
    from app.routes.content import content_bp
    from app.routes.forums import forums_bp
    from app.routes.threads import threads_bp
    from app.routes.replies import replies_bp
    from app.routes.assignments import assignments_bp
    from app.routes.submissions import submissions_bp
    from app.routes.grades import grades_bp
    from app.routes.reports import reports_bp

    for bp in [
        auth_bp, users_bp, courses_bp, enrollments_bp,
        calendar_events_bp, content_bp, forums_bp, threads_bp,
        replies_bp, assignments_bp, submissions_bp, grades_bp,
        reports_bp,
    ]:
        app.register_blueprint(bp)

    # --- Auto-apply migrations -------------------------------------------
    # On platforms without a docker-entrypoint-initdb.d hook (e.g.
    # Railway), the application itself must ensure the schema exists
    # before serving requests. All migrations are idempotent (CREATE
    # TABLE IF NOT EXISTS / CREATE OR REPLACE VIEW), so running them
    # on every startup is a no-op once the DB is fully migrated.
    # Set RUN_MIGRATIONS=0 to skip (used by the test suite, which
    # patches get_connection to an in-memory fake before create_app).
    if os.environ.get("RUN_MIGRATIONS", "1") == "1":
        try:
            from app.db.migrate import run_migrations
            run_migrations()
        except Exception:
            logger.exception("Migration runner failed during startup")
            raise

    # --- Health check -----------------------------------------------------
    @app.route("/api/health")
    def health():
        return {"status": "ok", "env": config.FLASK_ENV}

    # --- SPA (combined-image deploy only) --------------------------------
    if os.path.isdir(_FRONTEND_DIR):
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_spa(path):
            if path.startswith("api/"):
                return jsonify({"error": "not_found", "message": "Endpoint not found"}), 404
            target = os.path.join(_FRONTEND_DIR, path) if path else None
            if target and os.path.isfile(target):
                return send_from_directory(_FRONTEND_DIR, path)
            return send_from_directory(_FRONTEND_DIR, "index.html")

        logger.info("SPA static serving enabled from %s", _FRONTEND_DIR)

    logger.info("Flask app created — %d blueprints registered", len(app.blueprints))
    return app
