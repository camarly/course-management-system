"""
Redis cache key constants and builder functions.

Centralises every cache key string so that route handlers and
invalidation logic always reference the same key for the same resource.

Convention:  lms:<resource>:<identifier>
Example:     lms:courses:all
             lms:course:42
             lms:course:42:members

Owner: Camarly Thomas
"""

# TTL constants (seconds)
TTL_SHORT = 30
TTL_MEDIUM = 60
TTL_LONG = 300

# --- Static keys ---------------------------------------------------------
COURSES_ALL = "lms:courses:all"
USERS_ALL = "lms:users:all"

# --- Report keys ---------------------------------------------------------
REPORT_COURSES_50_PLUS = "lms:reports:courses-50-plus"
REPORT_STUDENTS_5_PLUS = "lms:reports:students-5-plus-courses"
REPORT_LECTURERS_3_PLUS = "lms:reports:lecturers-3-plus-courses"
REPORT_TOP10_COURSES = "lms:reports:top10-enrolled-courses"
REPORT_TOP10_STUDENTS = "lms:reports:top10-students-by-average"


# --- Builders ------------------------------------------------------------
def user_key(user_id: int) -> str:
    return f"lms:user:{user_id}"


def course_key(course_id: int) -> str:
    return f"lms:course:{course_id}"


def course_members_key(course_id: int) -> str:
    return f"lms:course:{course_id}:members"


def course_forums_key(course_id: int) -> str:
    return f"lms:course:{course_id}:forums"


def course_events_key(course_id: int) -> str:
    return f"lms:course:{course_id}:events"


def course_assignments_key(course_id: int) -> str:
    return f"lms:course:{course_id}:assignments"


def course_sections_key(course_id: int) -> str:
    return f"lms:course:{course_id}:sections"


def forum_threads_key(forum_id: int) -> str:
    return f"lms:forum:{forum_id}:threads"


def thread_key(thread_id: int) -> str:
    return f"lms:thread:{thread_id}"


def student_courses_key(student_id: int) -> str:
    return f"lms:student:{student_id}:courses"


def lecturer_courses_key(lecturer_id: int) -> str:
    return f"lms:lecturer:{lecturer_id}:courses"


def student_grades_key(student_id: int) -> str:
    return f"lms:student:{student_id}:grades"


def assignment_key(assignment_id: int) -> str:
    return f"lms:assignment:{assignment_id}"


def assignment_submissions_key(assignment_id: int) -> str:
    return f"lms:assignment:{assignment_id}:submissions"
