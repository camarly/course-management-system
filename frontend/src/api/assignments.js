/**
 * Assignments, Submissions, and Grades API module.
 *
 * Owner: Camarly Thomas
 */

import client from './client'

export async function getAssignments(courseId) {
  const { data } = await client.get(`/courses/${courseId}/assignments`)
  return data.data
}

export async function getAssignment(assignmentId) {
  const { data } = await client.get(`/assignments/${assignmentId}`)
  return data.data
}

export async function createAssignment(courseId, payload) {
  const { data } = await client.post(`/courses/${courseId}/assignments`, payload)
  return data.data
}

export async function submitAssignment(assignmentId, payload) {
  const { data } = await client.post(`/assignments/${assignmentId}/submit`, payload)
  return data.data
}

export async function getSubmissions(assignmentId) {
  const { data } = await client.get(`/assignments/${assignmentId}/submissions`)
  return data.data
}

export async function gradeSubmission(submissionId, payload) {
  const { data } = await client.post(`/submissions/${submissionId}/grade`, payload)
  return data.data
}

export async function getStudentGrades(studentId) {
  const { data } = await client.get(`/students/${studentId}/grades`)
  return data.data
}
