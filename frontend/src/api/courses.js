/**
 * Courses API module.
 *
 * Functions:
 *   getAllCourses()                         GET  /api/courses
 *   getCourse(courseId)                     GET  /api/courses/:id
 *   createCourse(payload)                   POST /api/courses
 *   getCourseMembers(courseId)              GET  /api/courses/:id/members
 *   enrollInCourse(courseId)                POST /api/courses/:id/enroll
 *   assignLecturer(courseId, lecturerId)    POST /api/courses/:id/assign-lecturer
 *   getStudentCourses(studentId)            GET  /api/students/:id/courses
 *   getLecturerCourses(lecturerId)          GET  /api/lecturers/:id/courses
 *   getCourseSections(courseId)             GET  /api/courses/:id/sections
 *   createSection(courseId, payload)        POST /api/courses/:id/sections
 *   addContentItem(sectionId, payload)      POST /api/sections/:id/items
 *
 * Owner: Camarly Thomas
 */

import client from './client'
