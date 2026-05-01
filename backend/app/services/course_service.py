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


def create_course(title, description, lecturer_id):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO courses (title, description, lecturer_id) "
                "VALUES (%s, %s, %s)",
                (title, description, lecturer_id),
            )
            course_id = cur.lastrowid
            conn.commit()

            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at, updated_at "
                "FROM courses WHERE id = %s",
                (course_id,),
            )
            return cur.fetchone()
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


def get_course_members(course_id):
    """
    Get all members of a course (students + lecturer).
    
    Args:
        course_id (int): The course ID
    
    Returns:
        dict: Dictionary with 'lecturer' and 'students' keys
              Returns None if course doesn't exist
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            
            cur.execute(
                "SELECT id FROM courses WHERE id = %s",
                (course_id,)
            )
            if not cur.fetchone():
                return None
            
            # Get lecturer info (if assigned)
            cur.execute(
                """
                SELECT u.id, u.name, u.email, u.role
                FROM users u
                JOIN courses c ON c.lecturer_id = u.id
                WHERE c.id = %s AND u.role = 'lecturer'
                """,
                (course_id,)
            )
            lecturer_result = cur.fetchone()
            
            lecturer = None
            if lecturer_result:
                lecturer = {
                    "id": lecturer_result["id"],
                    "name": lecturer_result["name"],
                    "email": lecturer_result["email"],
                    "role": lecturer_result["role"]
                }
            
            # Get all students enrolled in the course
            cur.execute(
                """
                SELECT u.id, u.name, u.email, u.role
                FROM users u
                JOIN course_enrollments ce ON ce.student_id = u.id
                WHERE ce.course_id = %s AND u.role = 'student'
                ORDER BY u.name
                """,
                (course_id,)
            )
            student_results = cur.fetchall()
            
            students = []
            for row in student_results:
                students.append({
                    "id": row["id"],
                    "name": row["name"],
                    "email": row["email"],
                    "role": row["role"]
                })
            
            return {
                "lecturer": lecturer,
                "students": students
            }
    finally:
        if conn:
            conn.close()

            