/**
 * Course card component.
 *
 * Owner: Camarly Thomas
 */

import { Link } from 'react-router-dom'

export default function CourseCard({ course, isEnrolled, onEnroll }) {
  return (
    <article className="course-card">
      <h3>
        <Link to={`/courses/${course.id}`}>{course.title}</Link>
      </h3>
      {course.description && <p className="muted">{course.description}</p>}
      <dl>
        <div>
          <dt>Lecturer</dt>
          <dd>{course.lecturer_name || course.lecturer_username || '—'}</dd>
        </div>
        <div>
          <dt>Enrolled</dt>
          <dd>{course.enrollment_count ?? course.member_count ?? '—'}</dd>
        </div>
      </dl>
      {onEnroll && (
        <button
          type="button"
          onClick={() => onEnroll(course.id)}
          disabled={isEnrolled}
        >
          {isEnrolled ? 'Enrolled' : 'Enroll'}
        </button>
      )}
    </article>
  )
}
