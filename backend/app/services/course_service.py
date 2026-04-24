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
    
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Insert the new course using %s placeholders 
            cur.execute(
                "INSERT INTO courses (title, description, lecturer_id) VALUES (%s, %s, %s)",
                (title, description, lecturer_id)
            )
            conn.commit()
            
            # Get the newly created course
            course_id = cur.lastrowid
            cur.execute(
                "SELECT id, title, description, lecturer_id, created_at, updated_at FROM courses WHERE id = %s",
                (course_id,)
            )
            result = cur.fetchone()
            
            # Convert to dict
            return {
                "id": result[0],
                "title": result[1],
                "description": result[2],
                "lecturer_id": result[3],
                "created_at": str(result[4]),
                "updated_at": str(result[5])
            }
    finally:
        if conn:
            conn.close()