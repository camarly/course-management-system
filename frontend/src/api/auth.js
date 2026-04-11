/**
 * Auth API module — JWT only, no Google OAuth.
 */

import client from './client'

export async function login(username, password) {
  const { data } = await client.post('/auth/login', { username, password })
  return data.data  // envelope: { data: { token, user }, message }
}

export async function register(username, email, password, role) {
  const { data } = await client.post('/auth/register', { username, email, password, role })
  return data.data
}

export async function me() {
  const { data } = await client.get('/users/me')
  return data.data
}
