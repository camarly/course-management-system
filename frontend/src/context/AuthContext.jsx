/**
 * Authentication context.
 *
 * Provides:
 *   currentUser   — decoded JWT payload { id, role } or null
 *   token         — raw JWT string from localStorage or null
 *   login(token)  — stores token, decodes payload, updates context
 *   logout()      — clears token from localStorage, resets context
 *   isRole(role)  — convenience helper, returns boolean
 *
 * Wrap the entire app (inside BrowserRouter) with <AuthProvider>.
 * Consume with the useAuth() hook exported from this file.
 *
 * Owner: Camarly Thomas
 */
