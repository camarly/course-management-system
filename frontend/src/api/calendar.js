/**
 * Calendar Events API module.
 *
 * Functions:
 *   getCourseEvents(courseId)               GET  /api/courses/:id/events
 *   createEvent(courseId, payload)          POST /api/courses/:id/events
 *   getStudentEvents(studentId, date)       GET  /api/students/:id/events?date=YYYY-MM-DD
 *
 * Owner: Camarly Thomas
 */

import client from './client'
