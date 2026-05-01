/**
 * Recursive reply tree component.
 *
 * Owner: Camarly Thomas
 */

import { useState } from 'react'
import { replyToReply, replyToThread } from '../api/forums'

function formatDate(value) {
  if (!value) return ''
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString()
}

function ReplyNode({ reply, threadId, depth, onReplyPosted }) {
  const [showForm, setShowForm] = useState(false)
  const [body, setBody] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!body.trim()) return
    setSubmitting(true)
    setError('')
    try {
      await replyToReply(reply.id, { body })
      setBody('')
      setShowForm(false)
      onReplyPosted?.()
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to post reply')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <li className="reply-node" style={{ marginLeft: depth * 16 }}>
      <div className="reply-body">
        <div className="reply-meta">
          <strong>{reply.created_by_username || `user #${reply.created_by}`}</strong>
          <span>{formatDate(reply.created_at)}</span>
        </div>
        <p>{reply.body}</p>
        <button type="button" className="link-button" onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancel' : 'Reply'}
        </button>
        {showForm && (
          <form onSubmit={handleSubmit} className="reply-form">
            <textarea
              value={body}
              onChange={(e) => setBody(e.target.value)}
              rows={3}
              required
              autoFocus
            />
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={submitting}>
              {submitting ? 'Posting…' : 'Post reply'}
            </button>
          </form>
        )}
      </div>
      {reply.children && reply.children.length > 0 && (
        <ul className="reply-children">
          {reply.children.map((child) => (
            <ReplyNode
              key={child.id}
              reply={child}
              threadId={threadId}
              depth={depth + 1}
              onReplyPosted={onReplyPosted}
            />
          ))}
        </ul>
      )}
    </li>
  )
}

export default function ReplyTree({ replies, threadId, onReplyPosted }) {
  const [body, setBody] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!body.trim()) return
    setSubmitting(true)
    setError('')
    try {
      await replyToThread(threadId, { body })
      setBody('')
      onReplyPosted?.()
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to post reply')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="reply-tree">
      {replies && replies.length > 0 ? (
        <ul className="reply-root">
          {replies.map((r) => (
            <ReplyNode
              key={r.id}
              reply={r}
              threadId={threadId}
              depth={0}
              onReplyPosted={onReplyPosted}
            />
          ))}
        </ul>
      ) : (
        <p className="muted">No replies yet.</p>
      )}
      <form onSubmit={handleSubmit} className="reply-form root">
        <h4>Reply to thread</h4>
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={4}
          required
        />
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? 'Posting…' : 'Post reply'}
        </button>
      </form>
    </div>
  )
}
