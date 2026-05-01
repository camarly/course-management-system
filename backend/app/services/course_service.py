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



def assign_lecturer_to_course(course_id, lecturer_id):
    """
    Assign a lecturer to a course.
    Enforces one-lecturer rule and the 5-course lecturer cap.
    Replaces any existing assignment.
    
    
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
                raise ValueError("Course not found")
            
            
            cur.execute(
                "SELECT id, role FROM users WHERE id = %s",
                (lecturer_id,)
            )
            user = cur.fetchone()
            if not user:
                raise ValueError("User not found")
            if user["role"] != 'lecturer':
                raise ValueError("User is not a lecturer")
            
            
            cur.execute(
                "SELECT lecturer_id FROM courses WHERE id = %s",
                (course_id,)
            )
            current = cur.fetchone()
            current_lecturer_id = current["lecturer_id"] if current else None
            
            
            if current_lecturer_id != lecturer_id:
                cur.execute(
                    "SELECT COUNT(*) as course_count FROM courses WHERE lecturer_id = %s",
                    (lecturer_id,)
                )
                result = cur.fetchone()
                course_count = result["course_count"] if result else 0
                
                if course_count >= 5:
                    raise ValueError(f"Lecturer already assigned to 5 courses (maximum)")
            
            
            cur.execute(
                "UPDATE courses SET lecturer_id = %s WHERE id = %s",
                (lecturer_id, course_id)
            )
            conn.commit()
            
           
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at FROM courses WHERE id = %s",
                (course_id,)
            )
            return cur.fetchone()
            
    finally:
        if conn:
            conn.close()



def get_courses_for_lecturer(lecturer_id):
    """
    Get all courses for a specific lecturer.
   
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
           
            cur.execute(
                """
                SELECT id, title, description, lecturer_id, created_at
                FROM courses
                WHERE lecturer_id = %s
                ORDER BY id
                """,
                (lecturer_id,)
            )
            results = cur.fetchall()
            
            
            courses = []
            for row in results:
                courses.append({
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "lecturer_id": row["lecturer_id"],
                    "created_at": str(row["created_at"]) if row["created_at"] else None
                })
            
            return courses
    finally:
        if conn:
            conn.close()