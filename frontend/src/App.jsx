/**
 * Root application component.
 * Defines the top-level route tree using react-router-dom.
 * Wraps the route tree with AuthContext so every child can access the current user.
 *
 * Public routes:  /login, /register
 * Protected routes (require JWT): everything else, guarded by <ProtectedRoute>
 */
