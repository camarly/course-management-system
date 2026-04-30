/**
 * Protected route wrapper.
 *
 * Owner: Camarly Thomas
 */

import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.jsx'

export default function ProtectedRoute({ allowedRoles, children }) {
  const { token, currentUser } = useAuth()
  if (!token) return <Navigate to="/login" replace />
  if (allowedRoles && currentUser && !allowedRoles.includes(currentUser.role)) {
    return <Navigate to="/unauthorised" replace />
  }
  return children
}
