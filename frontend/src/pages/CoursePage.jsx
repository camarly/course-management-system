/**
 * Course detail page.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getCourse, getCourseMembers } from '../api/courses'

const TABS = ['Overview', 'Content', 'Forums', 'Assignments', 'Members', 'Calendar']

export default function CoursePage() {
  const { courseId } = useParams()
  const [course, setCourse] = useState(null)
  const [members, setMembers] = useState(null)
  const [tab, setTab] = useState('Overview')
  const [error, setError] = useState('')

  useEffect(() => {
    getCourse(courseId).then(setCourse).catch((e) => {
      setError(e.response?.data?.message || 'Failed to load course')
    })
  }, [courseId])

  useEffect(() => {
    if (tab === 'Members' && members === null) {
      getCourseMembers(courseId)
        .then(setMembers)
        .catch((e) => setError(e.response?.data?.message || 'Failed to load members'))
    }
  }, [tab, courseId, members])

  if (error) return <div className="page"><p className="error">{error}</p></div>
  if (!course) return <div className="page"><p>Loading course…</p></div>

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>{course.title}</h1>
          <p className="muted">
            Lecturer: {course.lecturer_name || course.lecturer_username || 'Unassigned'}
          </p>
        </div>
      </header>
      {course.description && <p>{course.description}</p>}

      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t}
            className={tab === t ? 'tab active' : 'tab'}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </nav>

      <section className="tab-panel">
        {tab === 'Overview' && (
          <div>
            <p>Use the tabs above to view course content, forums, assignments, members, and calendar events.</p>
            <ul className="link-list">
              <li><Link to={`/courses/${courseId}/content`}>Open content page</Link></li>
              <li><Link to={`/courses/${courseId}/forums`}>Open forums</Link></li>
              <li><Link to={`/courses/${courseId}/assignments`}>Open assignments</Link></li>
            </ul>
          </div>
        )}
        {tab === 'Content' && (
          <p><Link to={`/courses/${courseId}/content`}>Go to full content page →</Link></p>
        )}
        {tab === 'Forums' && (
          <p><Link to={`/courses/${courseId}/forums`}>Go to forums →</Link></p>
        )}
        {tab === 'Assignments' && (
          <p><Link to={`/courses/${courseId}/assignments`}>Go to assignments →</Link></p>
        )}
        {tab === 'Calendar' && (
          <p><Link to={`/calendar?course=${courseId}`}>Go to calendar →</Link></p>
        )}
        {tab === 'Members' && (
          <div>
            {members === null && <p>Loading members…</p>}
            {members && members.length === 0 && <p className="muted">No members yet.</p>}
            {members && members.length > 0 && (
              <table className="grade-table">
                <thead>
                  <tr><th>Username</th><th>Email</th><th>Role</th></tr>
                </thead>
                <tbody>
                  {members.map((m) => (
                    <tr key={m.id}>
                      <td>{m.username}</td>
                      <td>{m.email}</td>
                      <td>{m.role}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </section>
    </div>
  )
}
