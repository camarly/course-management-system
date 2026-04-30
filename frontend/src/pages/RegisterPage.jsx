/**
 * Registration page.
 *
 * Owner: Camarly Thomas
 */

import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register as registerApi } from '../api/auth'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirm: '',
    role: 'student',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function update(field) {
    return (e) => setForm((f) => ({ ...f, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      await registerApi(form.username, form.email, form.password, form.role)
      navigate('/login', {
        replace: true,
        state: { justRegistered: true },
      })
    } catch (err) {
      setError(err.response?.data?.message || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-card">
      <h1>Create account</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Username
          <input value={form.username} onChange={update('username')} required autoFocus />
        </label>
        <label>
          Email
          <input type="email" value={form.email} onChange={update('email')} required />
        </label>
        <label>
          Password
          <input type="password" value={form.password} onChange={update('password')} required minLength={6} />
        </label>
        <label>
          Confirm password
          <input type="password" value={form.confirm} onChange={update('confirm')} required />
        </label>
        <label>
          Role
          <select value={form.role} onChange={update('role')}>
            <option value="student">Student</option>
            <option value="lecturer">Lecturer</option>
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={loading}>
          {loading ? 'Creating account…' : 'Register'}
        </button>
      </form>
      <p className="hint">
        Already registered? <Link to="/login">Sign in</Link>.
      </p>
    </div>
  )
}
