/**
 * Role-aware dashboard.
 */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { getStudentCourses, getLecturerCourses, getAllCourses } from '../api/courses'
import { getStudentEvents } from '../api/calendar'
import CourseCard from '../components/CourseCard.jsx'

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export default function DashboardPage() {
  const { currentUser } = useAuth()
  const [courses, setCourses] = useState([])
  const [events, setEvents] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!currentUser) return
    setLoading(true)
    setError('')

    async function load() {
      try {
        if (currentUser.role === 'student') {
          const [c, e] = await Promise.all([
            getStudentCourses(currentUser.id),
            getStudentEvents(currentUser.id, todayISO()).catch(() => []),
          ])
          setCourses(c || [])
          setEvents(e || [])
        } else if (currentUser.role === 'lecturer') {
          setCourses(await getLecturerCourses(currentUser.id))
        } else if (currentUser.role === 'admin') {
          setCourses(await getAllCourses())
        }
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to load dashboard')
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [currentUser])

  if (!currentUser) return null

  return (
    <div className="page">
      <header className="page-header">
        <h1>Welcome, {currentUser.username}</h1>
        <p className="muted">Signed in as {currentUser.role}</p>
      </header>

      {error && <p className="error">{error}</p>}
      {loading && <p>Loading…</p>}

      {currentUser.role === 'student' && (
        <>
          <section>
            <h2>Today's events</h2>
            {events.length === 0 ? (
              <p className="muted">Nothing scheduled for today.</p>
            ) : (
              <ul className="event-list">
                {events.map((ev) => (
                  <li key={ev.id}>
                    <strong>{ev.title}</strong> — {ev.course_title}
                    {ev.event_time && <span> @ {ev.event_time}</span>}
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section>
            <h2>My courses</h2>
            {courses.length === 0 ? (
              <p className="muted">
                You aren't enrolled in any courses yet. <Link to="/courses">Browse the catalogue</Link>.
              </p>
            ) : (
              <div className="card-grid">
                {courses.map((c) => (
                  <CourseCard key={c.id} course={c} />
                ))}
              </div>
            )}
          </section>
        </>
      )}

      {currentUser.role === 'lecturer' && (
        <section>
          <h2>Courses I teach</h2>
          {courses.length === 0 ? (
            <p className="muted">No courses assigned yet.</p>
          ) : (
            <div className="card-grid">
              {courses.map((c) => (
                <CourseCard key={c.id} course={c} />
              ))}
            </div>
          )}
        </section>
      )}

      {currentUser.role === 'admin' && (
        <section>
          <h2>All courses</h2>
          <p className="muted">{courses.length} total</p>
          <div className="card-grid">
            {courses.map((c) => (
              <CourseCard key={c.id} course={c} />
            ))}
          </div>
          <p>
            <Link to="/reports">View reports →</Link>
          </p>
        </section>
      )}
    </div>
  )
}
