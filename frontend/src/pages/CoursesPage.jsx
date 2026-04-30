/**
 * Course catalogue / listing.
 *
 * student  — Browse all courses, with Enroll button for ones not yet joined.
 * lecturer — Lists courses they teach.
 * admin    — Lists every course; can create new courses.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import {
  createCourse,
  enrollInCourse,
  getAllCourses,
  getLecturerCourses,
  getStudentCourses,
} from '../api/courses'
import CourseCard from '../components/CourseCard.jsx'

export default function CoursesPage() {
  const { currentUser } = useAuth()
  const [allCourses, setAllCourses] = useState([])
  const [enrolledIds, setEnrolledIds] = useState(new Set())
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({ title: '', description: '', lecturer_id: '' })

  async function refresh() {
    if (!currentUser) return
    setLoading(true)
    setError('')
    try {
      if (currentUser.role === 'student') {
        const [all, mine] = await Promise.all([
          getAllCourses(),
          getStudentCourses(currentUser.id),
        ])
        setAllCourses(all || [])
        setEnrolledIds(new Set((mine || []).map((c) => c.id)))
      } else if (currentUser.role === 'lecturer') {
        setAllCourses(await getLecturerCourses(currentUser.id))
      } else if (currentUser.role === 'admin') {
        setAllCourses(await getAllCourses())
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUser])

  async function handleEnroll(courseId) {
    try {
      await enrollInCourse(courseId)
      setEnrolledIds((prev) => new Set(prev).add(courseId))
    } catch (err) {
      setError(err.response?.data?.message || 'Enrollment failed')
    }
  }

  async function handleCreate(e) {
    e.preventDefault()
    try {
      const payload = {
        title: createForm.title,
        description: createForm.description || null,
      }
      if (createForm.lecturer_id) payload.lecturer_id = Number(createForm.lecturer_id)
      await createCourse(payload)
      setCreateForm({ title: '', description: '', lecturer_id: '' })
      setShowCreate(false)
      await refresh()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not create course')
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <h1>Courses</h1>
        {currentUser?.role === 'admin' && (
          <button onClick={() => setShowCreate((s) => !s)}>
            {showCreate ? 'Cancel' : 'New course'}
          </button>
        )}
      </header>

      {showCreate && (
        <form onSubmit={handleCreate} className="inline-form">
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
            Lecturer ID (optional)
            <input
              type="number"
              value={createForm.lecturer_id}
              onChange={(e) => setCreateForm({ ...createForm, lecturer_id: e.target.value })}
            />
          </label>
          <button type="submit">Create</button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Loading courses…</p>
      ) : (
        <div className="card-grid">
          {allCourses.map((c) => (
            <CourseCard
              key={c.id}
              course={c}
              isEnrolled={enrolledIds.has(c.id)}
              onEnroll={currentUser?.role === 'student' ? handleEnroll : undefined}
            />
          ))}
        </div>
      )}
    </div>
  )
}
