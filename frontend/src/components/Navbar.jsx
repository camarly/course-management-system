/**
 * Global navigation bar.
 *
 * Owner: Camarly Thomas
 */

import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

const linksByRole = {
  student: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/courses', label: 'Courses' },
    { to: '/calendar', label: 'Calendar' },
    { to: '/grades', label: 'My Grades' },
  ],
  lecturer: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/courses', label: 'My Courses' },
    { to: '/calendar', label: 'Calendar' },
  ],
  admin: [
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/courses', label: 'All Courses' },
    { to: '/reports', label: 'Reports' },
  ],
}

export default function Navbar() {
  const { currentUser, token, logout } = useAuth()
  const navigate = useNavigate()
  const role = currentUser?.role
  const links = role ? linksByRole[role] || [] : []

  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <nav className="navbar">
      <Link to="/dashboard" className="brand">CMS</Link>
      <div className="nav-links">
        {token ? (
          <>
            {links.map((l) => (
              <NavLink key={l.to} to={l.to} className={({ isActive }) => (isActive ? 'active' : '')}>
                {l.label}
              </NavLink>
            ))}
          </>
        ) : (
          <>
            <NavLink to="/login">Login</NavLink>
            <NavLink to="/register">Register</NavLink>
          </>
        )}
      </div>
      {token && (
        <div className="nav-user">
          <span>{currentUser?.username} <em>({role})</em></span>
          <button onClick={handleLogout}>Log out</button>
        </div>
      )}
    </nav>
  )
}
