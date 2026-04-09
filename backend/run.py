"""
Application entry point.

Imports the Flask app factory and exposes the `app` instance for Gunicorn
and the Flask CLI. Run directly for the development server.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
