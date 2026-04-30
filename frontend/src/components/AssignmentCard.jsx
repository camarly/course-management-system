/**
 * Assignment card component.
 *
 * Owner: Camarly Thomas
 */

function formatDate(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  return d.toLocaleDateString()
}

export default function AssignmentCard({ assignment, submission, grade, role, onSubmit }) {
  const submitted = !!submission
  const graded = !!grade

  return (
    <article className="assignment-card">
      <header>
        <h3>{assignment.title}</h3>
        <span className="weight">{assignment.weight}%</span>
      </header>
      {assignment.description && <p className="muted">{assignment.description}</p>}
      <p className="meta">Due {formatDate(assignment.due_date)}</p>

      {role === 'student' && (
        <div className="status">
          {graded && (
            <p className="grade">
              Grade: <strong>{grade.score}</strong>
              {grade.feedback && <em> — {grade.feedback}</em>}
            </p>
          )}
          {submitted && !graded && <p>Submitted on {formatDate(submission.submitted_at)} (awaiting grade)</p>}
          {!submitted && onSubmit && (
            <button type="button" onClick={() => onSubmit(assignment)}>Submit</button>
          )}
        </div>
      )}

      {(role === 'lecturer' || role === 'admin') && (
        <p className="meta">
          {assignment.submission_count ?? 0} submission(s)
        </p>
      )}
    </article>
  )
}
