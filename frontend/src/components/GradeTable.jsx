/**
 * Grade table component.
 *
 * Owner: Camarly Thomas
 */

export default function GradeTable({ grades, average }) {
  if (!grades || grades.length === 0) {
    return <p className="muted">No grades recorded yet.</p>
  }

  return (
    <table className="grade-table">
      <thead>
        <tr>
          <th>Course</th>
          <th>Assignment</th>
          <th>Score</th>
          <th>Weight</th>
          <th>Weighted</th>
          <th>Feedback</th>
        </tr>
      </thead>
      <tbody>
        {grades.map((g, idx) => {
          const weighted =
            g.score != null && g.weight != null
              ? ((Number(g.score) * Number(g.weight)) / 100).toFixed(2)
              : '—'
          return (
            <tr key={g.submission_id ?? `${g.course_title}-${g.assignment_title}-${idx}`}>
              <td>{g.course_title}</td>
              <td>{g.assignment_title}</td>
              <td>{g.score ?? '—'}</td>
              <td>{g.weight ?? '—'}</td>
              <td>{weighted}</td>
              <td>{g.feedback || ''}</td>
            </tr>
          )
        })}
      </tbody>
      {average != null && (
        <tfoot>
          <tr>
            <td colSpan={4}><strong>Overall average</strong></td>
            <td colSpan={2}><strong>{Number(average).toFixed(2)}</strong></td>
          </tr>
        </tfoot>
      )}
    </table>
  )
}
