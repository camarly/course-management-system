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
from app.services import reply_service


def create_thread(forum_id, title, body, created_by):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO threads (forum_id, title, body, created_by) "
                "VALUES (%s, %s, %s, %s)",
                (forum_id, title, body, created_by),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "forum_id": forum_id,
            "title": title,
            "body": body,
            "created_by": created_by,
        }
    finally:
        conn.close()


def list_threads(forum_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, forum_id, title, body, created_by, created_at "
                "FROM threads WHERE forum_id = %s "
                "ORDER BY created_at DESC",
                (forum_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_thread_with_replies(thread_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, forum_id, title, body, created_by, created_at "
                "FROM threads WHERE id = %s",
                (thread_id,),
            )
            thread = cur.fetchone()
            if not thread:
                return None
        thread["replies"] = reply_service.fetch_reply_tree(thread_id)
        return thread
    finally:
        conn.close()
