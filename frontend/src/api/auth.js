/**
 * Auth API module.
 *
 * Functions:
 *   register(username, password, role)  POST /api/auth/register
 *   login(username, password)           POST /api/auth/login
 *   googleLogin()                       GET  /api/auth/google/login  (redirect)
 *   adminCreateUser(payload)            POST /api/auth/admin/create-user
 *
 * Owner: Camarly Thomas
 */

import client from './client'
