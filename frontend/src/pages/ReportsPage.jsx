/**
 * Reports page. Admin only.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import {
  getCourses50Plus,
  getLecturers3PlusCourses,
  getStudents5PlusCourses,
  getTop10EnrolledCourses,
  getTop10StudentsByAverage,
} from '../api/reports'

const TABS = [
  { key: 'courses50', label: 'Courses ≥ 50 students', fetcher: getCourses50Plus },
  { key: 'students5', label: 'Students in ≥ 5 courses', fetcher: getStudents5PlusCourses },
  { key: 'lecturers3', label: 'Lecturers ≥ 3 courses', fetcher: getLecturers3PlusCourses },
  { key: 'topCourses', label: 'Top 10 enrolled courses', fetcher: getTop10EnrolledCourses },
  { key: 'topStudents', label: 'Top 10 students by avg', fetcher: getTop10StudentsByAverage },
]

function ReportTable({ rows }) {
  if (!rows || rows.length === 0) {
    return <p className="muted">No data.</p>
  }
  const cols = Object.keys(rows[0])
  return (
    <table className="grade-table">
      <thead>
        <tr>{cols.map((c) => <th key={c}>{c.replace(/_/g, ' ')}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {cols.map((c) => <td key={c}>{row[c] == null ? '' : String(row[c])}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default function ReportsPage() {
  const [activeKey, setActiveKey] = useState(TABS[0].key)
  const [cache, setCache] = useState({})
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (cache[activeKey]) return
    const tab = TABS.find((t) => t.key === activeKey)
    if (!tab) return
    setLoading(true)
    setError('')
    tab.fetcher()
      .then((data) => setCache((c) => ({ ...c, [activeKey]: data })))
      .catch((err) => setError(err.response?.data?.message || 'Failed to load report'))
      .finally(() => setLoading(false))
  }, [activeKey, cache])

  return (
    <div className="page">
      <header className="page-header">
        <h1>Reports</h1>
      </header>
      <nav className="tabs">
        {TABS.map((t) => (
          <button
            key={t.key}
            className={activeKey === t.key ? 'tab active' : 'tab'}
            onClick={() => setActiveKey(t.key)}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <section className="tab-panel">
        {error && <p className="error">{error}</p>}
        {loading && <p>Loading report…</p>}
        {!loading && cache[activeKey] && <ReportTable rows={cache[activeKey]} />}
      </section>
    </div>
  )
}
