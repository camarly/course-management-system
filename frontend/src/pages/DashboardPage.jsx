/**
 * Minimal dashboard — Phase 1 scope only.
 * Calls GET /api/users/me with the stored JWT and displays the profile.
 * Richer role-aware dashboards land in Phase 4.
 */

import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { me } from '../api/auth'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    me().then(setProfile).catch((e) => {
      setError(e.response?.data?.message || 'Failed to load profile')
    })
  }, [])

  function logout() {
    localStorage.removeItem('lms_token')
    localStorage.removeItem('lms_user')
    navigate('/login', { replace: true })
  }

  return (
    <div className="dashboard">
      <header>
        <h1>LMS Dashboard</h1>
        <button onClick={logout}>Log out</button>
      </header>
      {error && <p className="error">{error}</p>}
      {profile ? (
        <section>
          <h2>Welcome, {profile.username}</h2>
          <dl>
            <dt>ID</dt><dd>{profile.id}</dd>
            <dt>Email</dt><dd>{profile.email}</dd>
            <dt>Role</dt><dd>{profile.role}</dd>
          </dl>
        </section>
      ) : (
        !error && <p>Loading…</p>
      )}
    </div>
  )
}
