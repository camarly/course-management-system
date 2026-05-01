"""
Course service.

Responsibilities:
    - Create a course (admin)
    - List all courses
    - Get a single course by ID
    - Get all members of a course (students + lecturer)
    - Assign a lecturer to a course — enforces one-lecturer rule and
      the 5-course lecturer cap; replaces any existing assignment
    - Get all courses for a specific student
    - Get all courses for a specific lecturer

Owner: Tamarica Shaw
"""

from app.db.connection import get_connection


def create_course(title, description=None, lecturer_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO courses (title, description, lecturer_id) "
                "VALUES (%s, %s, %s)",
                (title, description, lecturer_id),
            )
            conn.commit()
            new_id = cur.lastrowid
        return {
            "id": new_id,
            "title": title,
            "description": description,
            "lecturer_id": lecturer_id,
        }
    finally:
        conn.close()


def list_courses():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at "
                "FROM courses ORDER BY id"
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_course(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at "
                "FROM courses WHERE id = %s",
                (course_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def get_members(course_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Lecturer
            cur.execute(
                "SELECT u.id, u.username, u.email, u.role "
                "FROM users u "
                "JOIN courses c ON c.lecturer_id = u.id "
                "WHERE c.id = %s",
                (course_id,),
            )
            members = cur.fetchall()

            # Enrolled students
            cur.execute(
                "SELECT u.id, u.username, u.email, u.role "
                "FROM users u "
                "JOIN enrollments e ON e.student_id = u.id "
                "WHERE e.course_id = %s "
                "ORDER BY u.id",
                (course_id,),
            )
            members.extend(cur.fetchall())
            return members
    finally:
        conn.close()


def assign_lecturer(course_id, lecturer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Verify lecturer exists and has role 'lecturer'
            cur.execute(
                "SELECT id, role FROM users WHERE id = %s",
                (lecturer_id,),
            )
            user = cur.fetchone()
            if not user:
                raise ValueError("not_found")
            if user["role"] != "lecturer":
                raise ValueError("not_lecturer")

            # Enforce 5-course cap (exclude the current course if already assigned)
            cur.execute(
                "SELECT COUNT(*) AS cnt FROM courses "
                "WHERE lecturer_id = %s AND id != %s",
                (lecturer_id, course_id),
            )
            if cur.fetchone()["cnt"] >= 5:
                raise ValueError("lecturer_limit")

            # Replace existing assignment
            cur.execute(
                "UPDATE courses SET lecturer_id = %s WHERE id = %s",
                (lecturer_id, course_id),
            )
            conn.commit()

            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at "
                "FROM courses WHERE id = %s",
                (course_id,),
            )
            return cur.fetchone()
    finally:
        conn.close()


def get_student_courses(student_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT c.id, c.title, c.description, c.lecturer_id, c.created_at "
                "FROM courses c "
                "JOIN enrollments e ON e.course_id = c.id "
                "WHERE e.student_id = %s "
                "ORDER BY c.id",
                (student_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()


def get_lecturer_courses(lecturer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at "
                "FROM courses WHERE lecturer_id = %s "
                "ORDER BY id",
                (lecturer_id,),
            )
            return cur.fetchall()
    finally:
        conn.close()
