/**
 * Calendar Events API module.
 *
 * Owner: Camarly Thomas
 */

import client from './client'

export async function getCourseEvents(courseId) {
  const { data } = await client.get(`/courses/${courseId}/events`)
  return data.data
}

export async function createEvent(courseId, payload) {
  const { data } = await client.post(`/courses/${courseId}/events`, payload)
  return data.data
}

export async function getStudentEvents(studentId, date) {
  const { data } = await client.get(`/students/${studentId}/events`, {
    params: { date },
  })
  return data.data
}
