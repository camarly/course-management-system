/**
 * Reports API module. All endpoints require the admin role.
 *
 * Functions:
 *   getCourses50Plus()              GET /api/reports/courses-50-plus
 *   getStudents5PlusCourses()       GET /api/reports/students-5-plus-courses
 *   getLecturers3PlusCourses()      GET /api/reports/lecturers-3-plus-courses
 *   getTop10EnrolledCourses()       GET /api/reports/top10-enrolled-courses
 *   getTop10StudentsByAverage()     GET /api/reports/top10-students-by-average
 *
 * Owner: Camarly Thomas
 */

import client from './client'
