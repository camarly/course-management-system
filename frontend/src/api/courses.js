/**
 * Courses API module.
 *
 * Owner: Camarly Thomas
 */

import client from './client'

export async function getAllCourses() {
  const { data } = await client.get('/courses')
  return data.data
}

export async function getCourse(courseId) {
  const { data } = await client.get(`/courses/${courseId}`)
  return data.data
}

export async function createCourse(payload) {
  const { data } = await client.post('/courses', payload)
  return data.data
}

export async function getCourseMembers(courseId) {
  const { data } = await client.get(`/courses/${courseId}/members`)
  return data.data
}

export async function enrollInCourse(courseId) {
  const { data } = await client.post(`/courses/${courseId}/enroll`)
  return data.data
}

export async function assignLecturer(courseId, lecturerId) {
  const { data } = await client.post(`/courses/${courseId}/assign-lecturer`, {
    lecturer_id: lecturerId,
  })
  return data.data
}

export async function getStudentCourses(studentId) {
  const { data } = await client.get(`/students/${studentId}/courses`)
  return data.data
}

export async function getLecturerCourses(lecturerId) {
  const { data } = await client.get(`/lecturers/${lecturerId}/courses`)
  return data.data
}

export async function getCourseSections(courseId) {
  const { data } = await client.get(`/courses/${courseId}/sections`)
  return data.data
}

export async function createSection(courseId, payload) {
  const { data } = await client.post(`/courses/${courseId}/sections`, payload)
  return data.data
}

export async function addContentItem(sectionId, payload) {
  const { data } = await client.post(`/sections/${sectionId}/items`, payload)
  return data.data
}
