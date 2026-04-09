"""
Reply service.

Responsibilities:
    - Create a reply directly to a thread (parent_reply_id = NULL)
    - Create a reply to a reply (parent_reply_id = <id>)
    - Fetch the full reply tree for a thread using a recursive CTE:

        WITH RECURSIVE reply_tree AS (
            SELECT * FROM replies WHERE thread_id = :tid AND parent_reply_id IS NULL
            UNION ALL
            SELECT r.* FROM replies r
            JOIN reply_tree rt ON r.parent_reply_id = rt.id
        )
        SELECT * FROM reply_tree;

    The CTE result is then assembled into a nested dict structure in Python.

Owner: Tramonique Wellington
"""

from app.db.connection import get_connection
