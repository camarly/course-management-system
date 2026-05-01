"""
Reply service.

Responsibilities:
    - Create a reply directly to a thread (parent_reply_id = NULL)
    - Create a reply to a reply (parent_reply_id = <id>)
    - Fetch the full reply tree for a thread using a recursive CTE

Owner: Tramonique Wellington
"""

from app.db.connection import get_connection


def create_reply(thread_id, body, created_by, parent_reply_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO replies (thread_id, parent_reply_id, body, created_by) "
                "VALUES (%s, %s, %s, %s)",
                (thread_id, parent_reply_id, body, created_by),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "thread_id": thread_id,
            "parent_reply_id": parent_reply_id,
            "body": body,
            "created_by": created_by,
        }
    finally:
        conn.close()


def fetch_reply_tree(thread_id):
    """Fetch all replies for a thread using a recursive CTE, then
    assemble them into a nested tree structure in Python."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "WITH RECURSIVE reply_tree AS ( "
                "  SELECT id, thread_id, parent_reply_id, body, created_by, created_at "
                "  FROM replies "
                "  WHERE thread_id = %s AND parent_reply_id IS NULL "
                "  UNION ALL "
                "  SELECT r.id, r.thread_id, r.parent_reply_id, r.body, r.created_by, r.created_at "
                "  FROM replies r "
                "  JOIN reply_tree rt ON r.parent_reply_id = rt.id "
                ") "
                "SELECT * FROM reply_tree ORDER BY created_at",
                (thread_id,),
            )
            flat_rows = cur.fetchall()
    finally:
        conn.close()

    return _build_tree(flat_rows)


def _build_tree(rows):
    """Convert a flat list of reply dicts into a nested tree."""
    by_id = {}
    roots = []
    for row in rows:
        row["children"] = []
        by_id[row["id"]] = row

    for row in rows:
        parent_id = row["parent_reply_id"]
        if parent_id is None:
            roots.append(row)
        else:
            parent = by_id.get(parent_id)
            if parent:
                parent["children"].append(row)
    return roots
