"""
Thread service.

Responsibilities:
    - Create a thread in a forum (title + opening body post)
    - List all threads in a forum
    - Get a single thread with its full nested reply tree
      (tree fetched via the recursive CTE pattern in reply_service)

Owner: Tramonique Wellington
"""

from app.db.connection import get_connection
