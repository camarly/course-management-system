/**
 * Assignments, Submissions, and Grades API module.
 *
 * Functions:
 *   getAssignments(courseId)                    GET  /api/courses/:id/assignments
 *   getAssignment(assignmentId)                 GET  /api/assignments/:id
 *   createAssignment(courseId, payload)         POST /api/courses/:id/assignments
 *   submitAssignment(assignmentId, payload)     POST /api/assignments/:id/submit
 *   getSubmissions(assignmentId)                GET  /api/assignments/:id/submissions
 *   gradeSubmission(submissionId, payload)      POST /api/submissions/:id/grade
 *   getStudentGrades(studentId)                 GET  /api/students/:id/grades
 *
 * Owner: Camarly Thomas
 */

import client from './client'
