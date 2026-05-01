/**
 * Thread list component.
 *
 * Owner: Camarly Thomas
 */

import { Link } from 'react-router-dom'

function formatDate(value) {
  if (!value) return ''
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString()
}

export default function ThreadList({ threads, forumId }) {
  if (!threads || threads.length === 0) {
    return <p className="muted">No threads yet — be the first to post.</p>
  }

  return (
    <ul className="thread-list">
      {threads.map((t) => (
        <li key={t.id}>
          <Link to={`/forums/${forumId}/threads/${t.id}`} className="thread-title">
            {t.title}
          </Link>
          <div className="thread-meta">
            <span>by {t.created_by_username || `user #${t.created_by}`}</span>
            <span>{t.reply_count ?? 0} repl{(t.reply_count ?? 0) === 1 ? 'y' : 'ies'}</span>
            <span>{formatDate(t.created_at)}</span>
          </div>
        </li>
      ))}
    </ul>
  )
}
