-- Migration 003: enrollments
-- Junction table linking students to courses.
-- The unique constraint prevents duplicate enrollments.
-- Business-rule caps (6 per student, 5 per lecturer) are enforced in application code.

CREATE TABLE IF NOT EXISTS enrollments (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    student_id  INT UNSIGNED  NOT NULL,
    course_id   INT UNSIGNED  NOT NULL,
    enrolled_at TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_enrollment UNIQUE (student_id, course_id),
    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (student_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE,
    INDEX idx_enrollments_student (student_id),
    INDEX idx_enrollments_course  (course_id)
);
