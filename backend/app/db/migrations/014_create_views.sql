-- Migration 014: report views
-- Five read-only views used exclusively by the /api/reports/* endpoints.
-- Never query these views from any other service.

-- View 1: Courses with 50 or more enrolled students
CREATE OR REPLACE VIEW vw_courses_50_plus AS
SELECT
    c.id            AS course_id,
    c.title         AS course_title,
    COUNT(e.id)     AS enrollment_count
FROM courses     c
JOIN enrollments e ON e.course_id = c.id
GROUP BY c.id, c.title
HAVING COUNT(e.id) >= 50;


-- View 2: Students enrolled in 5 or more courses
CREATE OR REPLACE VIEW vw_students_5_plus_courses AS
SELECT
    u.id            AS student_id,
    u.username,
    u.email,
    COUNT(e.id)     AS course_count
FROM users       u
JOIN enrollments e ON e.student_id = u.id
WHERE u.role = 'student'
GROUP BY u.id, u.username, u.email
HAVING COUNT(e.id) >= 5;


-- View 3: Lecturers teaching 3 or more courses
CREATE OR REPLACE VIEW vw_lecturers_3_plus_courses AS
SELECT
    u.id            AS lecturer_id,
    u.username,
    u.email,
    COUNT(c.id)     AS course_count
FROM users    u
JOIN courses  c ON c.lecturer_id = u.id
WHERE u.role = 'lecturer'
GROUP BY u.id, u.username, u.email
HAVING COUNT(c.id) >= 3;


-- View 4: Top 10 most enrolled courses
CREATE OR REPLACE VIEW vw_top10_enrolled_courses AS
SELECT
    c.id            AS course_id,
    c.title         AS course_title,
    COUNT(e.id)     AS enrollment_count
FROM courses     c
JOIN enrollments e ON e.course_id = c.id
GROUP BY c.id, c.title
ORDER BY enrollment_count DESC
LIMIT 10;


-- View 5: Top 10 students by highest overall average grade
CREATE OR REPLACE VIEW vw_top10_students_by_average AS
SELECT
    u.id            AS student_id,
    u.username,
    u.email,
    sa.average_grade
FROM users           u
JOIN student_averages sa ON sa.student_id = u.id
WHERE u.role = 'student'
ORDER BY sa.average_grade DESC
LIMIT 10;
