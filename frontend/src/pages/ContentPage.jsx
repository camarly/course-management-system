/**
 * Course content page.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { addContentItem, createSection, getCourseSections } from '../api/courses'

export default function ContentPage() {
  const { courseId } = useParams()
  const { currentUser } = useAuth()
  const [sections, setSections] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const [showSectionForm, setShowSectionForm] = useState(false)
  const [sectionTitle, setSectionTitle] = useState('')

  const [itemFor, setItemFor] = useState(null)
  const [itemForm, setItemForm] = useState({ title: '', item_type: 'link', url: '' })

  async function load() {
    setLoading(true)
    setError('')
    try {
      const list = await getCourseSections(courseId)
      setSections(list || [])
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load content')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId])

  async function handleAddSection(e) {
    e.preventDefault()
    try {
      await createSection(courseId, { title: sectionTitle, position: sections.length })
      setSectionTitle('')
      setShowSectionForm(false)
      await load()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not add section')
    }
  }

  async function handleAddItem(e) {
    e.preventDefault()
    if (!itemFor) return
    try {
      await addContentItem(itemFor.id, itemForm)
      setItemFor(null)
      setItemForm({ title: '', item_type: 'link', url: '' })
      await load()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not add item')
    }
  }

  const isLecturer = currentUser?.role === 'lecturer'

  return (
    <div className="page">
      <header className="page-header">
        <h1>Course content</h1>
        {isLecturer && (
          <button onClick={() => setShowSectionForm((s) => !s)}>
            {showSectionForm ? 'Cancel' : 'Add section'}
          </button>
        )}
      </header>

      {showSectionForm && (
        <form onSubmit={handleAddSection} className="inline-form">
          <label>
            Section title
            <input value={sectionTitle} onChange={(e) => setSectionTitle(e.target.value)} required />
          </label>
          <button type="submit">Create section</button>
        </form>
      )}

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p>Loading content…</p>
      ) : sections.length === 0 ? (
        <p className="muted">No content sections yet.</p>
      ) : (
        <ul className="section-list">
          {sections.map((s) => (
            <li key={s.id} className="section">
              <header>
                <h2>{s.title}</h2>
                {isLecturer && (
                  <button onClick={() => setItemFor(s)}>Add item</button>
                )}
              </header>
              {(s.items || []).length === 0 ? (
                <p className="muted">No items.</p>
              ) : (
                <ul className="content-items">
                  {s.items.map((it) => (
                    <li key={it.id}>
                      <span className="badge">{it.item_type}</span>
                      <a href={it.url} target="_blank" rel="noopener noreferrer">
                        {it.title}
                      </a>
                    </li>
                  ))}
                </ul>
              )}
            </li>
          ))}
        </ul>
      )}

      {itemFor && (
        <div className="modal-backdrop" onClick={() => setItemFor(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Add item to: {itemFor.title}</h3>
            <form onSubmit={handleAddItem}>
              <label>
                Title
                <input
                  value={itemForm.title}
                  onChange={(e) => setItemForm({ ...itemForm, title: e.target.value })}
                  required
                  autoFocus
                />
              </label>
              <label>
                Type
                <select
                  value={itemForm.item_type}
                  onChange={(e) => setItemForm({ ...itemForm, item_type: e.target.value })}
                >
                  <option value="link">Link</option>
                  <option value="file">File</option>
                  <option value="slides">Slides</option>
                </select>
              </label>
              <label>
                URL
                <input
                  type="url"
                  value={itemForm.url}
                  onChange={(e) => setItemForm({ ...itemForm, url: e.target.value })}
                  required
                />
              </label>
              <div className="modal-actions">
                <button type="button" onClick={() => setItemFor(null)}>Cancel</button>
                <button type="submit">Add item</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
