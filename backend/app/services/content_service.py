"""
Course content service.

Responsibilities:
    - Create a named content section for a course
    - Add a content item (link / file / slide) to a section
    - List all sections for a course, each with its ordered content items

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection


def create_section(course_id, title, position=0):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO content_sections (course_id, title, position) "
                "VALUES (%s, %s, %s)",
                (course_id, title, position),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "course_id": course_id,
            "title": title,
            "position": position,
        }
    finally:
        conn.close()


def add_item(section_id, title, item_type, url, position=0):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO content_items (section_id, title, item_type, url, position) "
                "VALUES (%s, %s, %s, %s, %s)",
                (section_id, title, item_type, url, position),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "section_id": section_id,
            "title": title,
            "item_type": item_type,
            "url": url,
            "position": position,
        }
    finally:
        conn.close()


def list_sections_with_items(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, course_id, title, position, created_at "
                "FROM content_sections WHERE course_id = %s "
                "ORDER BY position",
                (course_id,),
            )
            sections = cur.fetchall()

            for section in sections:
                cur.execute(
                    "SELECT id, section_id, title, item_type, url, position, created_at "
                    "FROM content_items WHERE section_id = %s "
                    "ORDER BY position",
                    (section["id"],),
                )
                section["items"] = cur.fetchall()

            return sections
    finally:
        conn.close()
