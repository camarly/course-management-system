/**
 * Axios base client.
 *
 * Creates a pre-configured Axios instance with:
 *   - baseURL pointing to /api
 *   - Request interceptor: attaches Authorization: Bearer <token> from localStorage
 *   - Response interceptor: redirects to /login on 401
 *
 * All other API modules import and use this instance — never call axios directly.
 *
 * Owner: Camarly Thomas
 */
