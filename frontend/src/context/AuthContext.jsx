/**
 * Authentication context.
 *
 * Owner: Camarly Thomas
 */

import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AuthContext = createContext(null)

function readUser() {
  const raw = localStorage.getItem('lms_user')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('lms_token'))
  const [currentUser, setCurrentUser] = useState(readUser)

  useEffect(() => {
    function onStorage() {
      setToken(localStorage.getItem('lms_token'))
      setCurrentUser(readUser())
    }
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  function login({ token: nextToken, user }) {
    localStorage.setItem('lms_token', nextToken)
    localStorage.setItem('lms_user', JSON.stringify(user))
    setToken(nextToken)
    setCurrentUser(user)
  }

  function logout() {
    localStorage.removeItem('lms_token')
    localStorage.removeItem('lms_user')
    setToken(null)
    setCurrentUser(null)
  }

  function isRole(...roles) {
    return !!currentUser && roles.includes(currentUser.role)
  }

  const value = useMemo(
    () => ({ token, currentUser, login, logout, isRole }),
    [token, currentUser],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
