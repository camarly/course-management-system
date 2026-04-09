-- Migration 010: assignments
-- Assessments created by a lecturer for a course.
-- weight is a percentage (0.00–100.00) used to compute the final average.

CREATE TABLE IF NOT EXISTS assignments (
    id          INT UNSIGNED    AUTO_INCREMENT PRIMARY KEY,
    course_id   INT UNSIGNED    NOT NULL,
    title       VARCHAR(255)    NOT NULL,
    description TEXT            NULL,
    due_date    DATETIME        NOT NULL,
    weight      DECIMAL(5,2)    NOT NULL DEFAULT 0.00,
    created_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                         ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_assignments_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE,
    INDEX idx_assignments_course (course_id)
);
