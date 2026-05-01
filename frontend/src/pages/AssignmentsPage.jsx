/**
 * Assignments page.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import {
  createAssignment,
  getAssignments,
  getStudentGrades,
  submitAssignment,
} from '../api/assignments'
import AssignmentCard from '../components/AssignmentCard.jsx'

export default function AssignmentsPage() {
  const { courseId } = useParams()
  const { currentUser } = useAuth()
  const [assignments, setAssignments] = useState([])
  const [gradeMap, setGradeMap] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    due_date: '',
    weight: 10,
  })
  const [submitFor, setSubmitFor] = useState(null)
  const [submitUrl, setSubmitUrl] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const list = await getAssignments(courseId)
      setAssignments(list || [])
      if (currentUser?.role === 'student') {
        const grades = await getStudentGrades(currentUser.id).catch(() => [])
        const m = {}
        grades.forEach((g) => {
          if (g.assignment_id) m[g.assignment_id] = g
        })
        setGradeMap(m)
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load assignments')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId, currentUser?.id])

  async function handleCreate(e) {
    e.preventDefault()
    try {
      await createAssignment(courseId, {
        title: createForm.title,
        description: createForm.description || null,
        due_date: createForm.due_date,
        weight: Number(createForm.weight),
      })
      setShowCreate(false)
      setCreateForm({ title: '', description: '', due_date: '', weight: 10 })
      await load()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not create assignment')
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!submitFor) return
    try {
      await submitAssignment(submitFor.id, { file_url: submitUrl })
      setSubmitFor(null)
      setSubmitUrl('')
      await load()
    } catch (err) {
      setError(err.response?.data?.message || 'Submission failed')
    }
  }

  const role = currentUser?.role
  const canCreate = role === 'lecturer' || role === 'admin'

  return (
    <div className="page">
      <header className="page-header">
        <h1>Assignments</h1>
        {canCreate && (
          <button onClick={() => setShowCreate((s) => !s)}>
            {showCreate ? 'Cancel' : 'New assignment'}
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
            Due date
            <input
              type="date"
              value={createForm.due_date}
              onChange={(e) => setCreateForm({ ...createForm, due_date: e.target.value })}
              required
            />
          </label>
          <label>
            Weight (%)
            <input
              type="number"
              min="0"
              max="100"
              value={createForm.weight}
              onChange={(e) => setCreateForm({ ...createForm, weight: e.target.value })}
              required
            />
          </label>
          <button type="submit">Create assignment</button>
        </form>
      )}

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p>Loading assignments…</p>
      ) : assignments.length === 0 ? (
        <p className="muted">No assignments yet for this course.</p>
      ) : (
        <div className="card-grid">
          {assignments.map((a) => (
            <AssignmentCard
              key={a.id}
              assignment={a}
              submission={a.submission || null}
              grade={gradeMap[a.id] || a.grade || null}
              role={role}
              onSubmit={role === 'student' ? setSubmitFor : undefined}
            />
          ))}
        </div>
      )}

      {submitFor && (
        <div className="modal-backdrop" onClick={() => setSubmitFor(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Submit: {submitFor.title}</h3>
            <form onSubmit={handleSubmit}>
              <label>
                File URL
                <input
                  type="url"
                  value={submitUrl}
                  onChange={(e) => setSubmitUrl(e.target.value)}
                  placeholder="https://…"
                  required
                  autoFocus
                />
              </label>
              <div className="modal-actions">
                <button type="button" onClick={() => setSubmitFor(null)}>Cancel</button>
                <button type="submit">Submit</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
