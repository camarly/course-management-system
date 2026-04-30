/**
 * Thread detail page.
 *
 * Owner: Camarly Thomas
 */

import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getThread } from '../api/forums'
import ReplyTree from '../components/ReplyTree.jsx'

function formatDate(value) {
  if (!value) return ''
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString()
}

export default function ThreadPage() {
  const { threadId } = useParams()
  const navigate = useNavigate()
  const [thread, setThread] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    try {
      setThread(await getThread(threadId))
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load thread')
    }
  }, [threadId])

  useEffect(() => {
    load()
  }, [load])

  if (error) return <div className="page"><p className="error">{error}</p></div>
  if (!thread) return <div className="page"><p>Loading thread…</p></div>

  return (
    <div className="page">
      <p className="breadcrumb">
        <button type="button" className="link-button" onClick={() => navigate(-1)}>← Back</button>
      </p>
      <header className="page-header">
        <div>
          <h1>{thread.title}</h1>
          <p className="muted">
            Started by {thread.created_by_username || `user #${thread.created_by}`} · {formatDate(thread.created_at)}
          </p>
        </div>
      </header>
      <article className="thread-body">
        <p>{thread.body}</p>
      </article>
      <ReplyTree
        replies={thread.replies || []}
        threadId={Number(threadId)}
        onReplyPosted={load}
      />
    </div>
  )
}
