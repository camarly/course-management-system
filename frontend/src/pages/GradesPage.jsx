/**
 * Student grades page.
 *
 * Owner: Camarly Thomas
 */

import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext.jsx'
import { getStudentGrades } from '../api/assignments'
import GradeTable from '../components/GradeTable.jsx'

function average(grades) {
  const weighted = grades.filter((g) => g.score != null && g.weight != null)
  if (weighted.length === 0) return null
  const totalWeight = weighted.reduce((s, g) => s + Number(g.weight), 0)
  if (totalWeight === 0) return null
  const total = weighted.reduce((s, g) => s + Number(g.score) * Number(g.weight), 0)
  return total / totalWeight
}

export default function GradesPage() {
  const { currentUser } = useAuth()
  const [grades, setGrades] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!currentUser) return
    setLoading(true)
    getStudentGrades(currentUser.id)
      .then((g) => setGrades(g || []))
      .catch((err) => setError(err.response?.data?.message || 'Failed to load grades'))
      .finally(() => setLoading(false))
  }, [currentUser])

  return (
    <div className="page">
      <header className="page-header">
        <h1>My grades</h1>
      </header>
      {error && <p className="error">{error}</p>}
      {loading ? <p>Loading…</p> : <GradeTable grades={grades} average={average(grades)} />}
    </div>
  )
}
