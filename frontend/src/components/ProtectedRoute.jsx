/**
 * Protected route wrapper.
 *
 * Reads the current user from AuthContext.
 * If no token is present, redirects to /login.
 * If an allowedRoles prop is supplied, redirects to /unauthorised
 * when the user's role is not in the list.
 *
 * Usage:
 *   <ProtectedRoute allowedRoles={['admin', 'lecturer']}>
 *     <SomePage />
 *   </ProtectedRoute>
 *
 * Owner: Camarly Thomas
 */
