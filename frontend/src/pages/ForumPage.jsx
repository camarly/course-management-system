/**
 * Forum page — lists forums for a course, and threads inside a chosen forum.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'
import { createForum, createThread, getForums, getThreads } from '../api/forums'
import ThreadList from '../components/ThreadList.jsx'

export default function ForumPage() {
  const { courseId } = useParams()
  const { currentUser } = useAuth()
  const [forums, setForums] = useState([])
  const [activeForum, setActiveForum] = useState(null)
  const [threads, setThreads] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  const [showForumForm, setShowForumForm] = useState(false)
  const [forumForm, setForumForm] = useState({ title: '', description: '' })

  const [showThreadForm, setShowThreadForm] = useState(false)
  const [threadForm, setThreadForm] = useState({ title: '', body: '' })

  async function loadForums() {
    setLoading(true)
    setError('')
    try {
      const list = await getForums(courseId)
      setForums(list || [])
      if (list && list.length > 0 && !activeForum) {
        setActiveForum(list[0])
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load forums')
    } finally {
      setLoading(false)
    }
  }

  async function loadThreads(forumId) {
    try {
      setThreads(await getThreads(forumId))
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load threads')
    }
  }

  useEffect(() => {
    loadForums()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [courseId])

  useEffect(() => {
    if (activeForum) loadThreads(activeForum.id)
  }, [activeForum])

  async function handleCreateForum(e) {
    e.preventDefault()
    try {
      await createForum(courseId, forumForm)
      setForumForm({ title: '', description: '' })
      setShowForumForm(false)
      await loadForums()
    } catch (err) {
      setError(err.response?.data?.message || 'Could not create forum')
    }
  }

  async function handleCreateThread(e) {
    e.preventDefault()
    if (!activeForum) return
    try {
      await createThread(activeForum.id, threadForm)
      setThreadForm({ title: '', body: '' })
      setShowThreadForm(false)
      await loadThreads(activeForum.id)
    } catch (err) {
      setError(err.response?.data?.message || 'Could not create thread')
    }
  }

  const canCreateForum = currentUser?.role === 'lecturer' || currentUser?.role === 'admin'

  return (
    <div className="page">
      <header className="page-header">
        <h1>Forums</h1>
        {canCreateForum && (
          <button onClick={() => setShowForumForm((s) => !s)}>
            {showForumForm ? 'Cancel' : 'New forum'}
          </button>
        )}
      </header>

      {showForumForm && (
        <form onSubmit={handleCreateForum} className="inline-form">
          <label>
            Title
            <input
              value={forumForm.title}
              onChange={(e) => setForumForm({ ...forumForm, title: e.target.value })}
              required
            />
          </label>
          <label>
            Description
            <textarea
              value={forumForm.description}
              onChange={(e) => setForumForm({ ...forumForm, description: e.target.value })}
              rows={2}
            />
          </label>
          <button type="submit">Create forum</button>
        </form>
      )}

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Loading forums…</p>
      ) : forums.length === 0 ? (
        <p className="muted">No forums yet for this course.</p>
      ) : (
        <div className="forum-layout">
          <aside>
            <h3>Forums</h3>
            <ul className="forum-list">
              {forums.map((f) => (
                <li key={f.id}>
                  <button
                    type="button"
                    className={activeForum?.id === f.id ? 'active' : ''}
                    onClick={() => setActiveForum(f)}
                  >
                    {f.title}
                  </button>
                </li>
              ))}
            </ul>
          </aside>
          <section>
            {activeForum ? (
              <>
                <header className="page-header">
                  <h2>{activeForum.title}</h2>
                  <button onClick={() => setShowThreadForm((s) => !s)}>
                    {showThreadForm ? 'Cancel' : 'New thread'}
                  </button>
                </header>
                {activeForum.description && <p className="muted">{activeForum.description}</p>}

                {showThreadForm && (
                  <form onSubmit={handleCreateThread} className="inline-form">
                    <label>
                      Thread title
                      <input
                        value={threadForm.title}
                        onChange={(e) => setThreadForm({ ...threadForm, title: e.target.value })}
                        required
                      />
                    </label>
                    <label>
                      Opening post
                      <textarea
                        value={threadForm.body}
                        onChange={(e) => setThreadForm({ ...threadForm, body: e.target.value })}
                        rows={4}
                        required
                      />
                    </label>
                    <button type="submit">Post thread</button>
                  </form>
                )}

                <ThreadList threads={threads} forumId={activeForum.id} />
              </>
            ) : (
              <p className="muted">Select a forum from the list.</p>
            )}
          </section>
        </div>
      )}
    </div>
  )
}
