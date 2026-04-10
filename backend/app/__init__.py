"""
Flask application factory.

create_app() initialises the Flask app, loads configuration,
registers CORS, and mounts all route blueprints.
"""

import logging
from flask import Flask
from flask_cors import CORS
from app import config

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

    # --- Health check -----------------------------------------------------
    @app.route("/api/health")
    def health():
        return {"status": "ok", "env": config.FLASK_ENV}

    logger.info("Flask app created — %d blueprints registered", len(app.blueprints))
    return app
