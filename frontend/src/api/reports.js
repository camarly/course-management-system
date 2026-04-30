/**
 * Reports API module. All endpoints require the admin role.
 *
 * Owner: Camarly Thomas
 */

import client from './client'

export async function getCourses50Plus() {
  const { data } = await client.get('/reports/courses-50-plus')
  return data.data
}

export async function getStudents5PlusCourses() {
  const { data } = await client.get('/reports/students-5-plus-courses')
  return data.data
}

export async function getLecturers3PlusCourses() {
  const { data } = await client.get('/reports/lecturers-3-plus-courses')
  return data.data
}

export async function getTop10EnrolledCourses() {
  const { data } = await client.get('/reports/top10-enrolled-courses')
  return data.data
}

export async function getTop10StudentsByAverage() {
  const { data } = await client.get('/reports/top10-students-by-average')
  return data.data
}
