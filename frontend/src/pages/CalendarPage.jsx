/**
 * Calendar page.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { createEvent, getCourseEvents, getStudentEvents } from '../api/calendar'
import { getLecturerCourses } from '../api/courses'

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export default function CalendarPage() {
  const { currentUser } = useAuth()
  const [searchParams] = useSearchParams()
  const courseFilter = searchParams.get('course')
  const [date, setDate] = useState(todayISO())
  const [events, setEvents] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const [lecturerCourses, setLecturerCourses] = useState([])
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({
    course_id: '',
    title: '',
    description: '',
    event_date: todayISO(),
    event_time: '',
  })

  async function load() {
    setLoading(true)
    setError('')
    try {
      if (currentUser.role === 'student') {
        const list = await getStudentEvents(currentUser.id, date)
        setEvents(list || [])
      } else if (courseFilter) {
        const list = await getCourseEvents(courseFilter)
        setEvents(list || [])
      } else if (currentUser.role === 'lecturer') {
        const courses = await getLecturerCourses(currentUser.id)
        setLecturerCourses(courses || [])
        const all = await Promise.all((courses || []).map((c) => getCourseEvents(c.id).catch(() => [])))
        setEvents(all.flat())
      } else {
        setEvents([])
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load events')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (currentUser) load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser?.id, currentUser?.role, date, courseFilter])

  async function handleCreate(e) {
    e.preventDefault()
    if (!createForm.course_id) {
      setError('Pick a course')
      return
    }
    try {
      await createEvent(createForm.course_id, {
        title: createForm.title,
        description: createForm.description || null,
        event_date: createForm.event_date,
        event_time: createForm.event_time || null,
      })
      setShowCreate(false)
      setCreateForm({
        course_id: '',
        title: '',
        description: '',
        event_date: todayISO(),
        event_time: '',
      })
      await load()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not create event')
    }
  }

  if (!currentUser) return null

  return (
    <div className="page">
      <header className="page-header">
        <h1>Calendar</h1>
        {(currentUser.role === 'lecturer' || currentUser.role === 'admin') && (
          <button onClick={() => setShowCreate((s) => !s)}>
            {showCreate ? 'Cancel' : 'New event'}
          </button>
        )}
      </header>

      {currentUser.role === 'student' && (
        <div className="filters">
          <label>
            Date
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </label>
        </div>
      )}

      {showCreate && (
        <form onSubmit={handleCreate} className="inline-form">
          <label>
            Course
            <select
              value={createForm.course_id}
              onChange={(e) => setCreateForm({ ...createForm, course_id: e.target.value })}
              required
            >
              <option value="">Select a course…</option>
              {lecturerCourses.map((c) => (
                <option key={c.id} value={c.id}>{c.title}</option>
              ))}
            </select>
          </label>
          <label>
            Title
            <input
              value={createForm.title}
              onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              rows={2}
            />
          </label>
          <label>
            Date
            <input
              type="date"
              value={createForm.event_date}
              onChange={(e) => setCreateForm({ ...createForm, event_date: e.target.value })}
              required
            />
          </label>
          <label>
            Time
            <input
              type="time"
              value={createForm.event_time}
              onChange={(e) => setCreateForm({ ...createForm, event_time: e.target.value })}
            />
          </label>
          <button type="submit">Create event</button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Loading events…</p>
      ) : events.length === 0 ? (
        <p className="muted">No events to display.</p>
      ) : (
        <ul className="event-list">
          {events.map((ev) => (
            <li key={ev.id}>
              <div>
                <strong>{ev.title}</strong>
                {ev.course_title && <span className="muted"> — {ev.course_title}</span>}
              </div>
              <div className="muted">
                {ev.event_date}{ev.event_time ? ` @ ${ev.event_time}` : ''}
              </div>
              {ev.description && <p>{ev.description}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
