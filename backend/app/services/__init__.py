"""
Services package.

Each module contains the raw SQL business logic for one resource domain.
Services are called by route handlers and must not import from routes.
All database access uses app.db.connection.get_connection().
"""
