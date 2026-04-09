"""
Notification Celery tasks (bonus).

Tasks:
    notify_grade_posted(student_id, assignment_id, score)
        Sends an in-app or email notification when a grade is posted.

    notify_new_thread(course_id, thread_id)
        Notifies course members when a new thread is created.

Owner: Camarly Thomas
"""

from app.tasks.celery_app import celery_app
