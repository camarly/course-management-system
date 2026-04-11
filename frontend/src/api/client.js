/**
 * Axios base client.
 *
 * Pre-configured Axios instance used by every API module:
 *   - baseURL: /api  (proxied by Vite dev server or Nginx in prod)
 *   - Attaches Authorization: Bearer <token> from localStorage
 *   - On 401, clears the token and redirects to /login
 */

import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('lms_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('lms_token')
      if (window.location.pathname !== '/login') {
        window.location.assign('/login')
      }
    }
    return Promise.reject(error)
  },
)

export default client
