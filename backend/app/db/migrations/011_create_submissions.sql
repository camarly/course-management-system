-- Migration 011: submissions
-- A student's submitted work for an assignment.
-- The unique constraint prevents multiple submissions per student per assignment.

CREATE TABLE IF NOT EXISTS submissions (
    id             INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    assignment_id  INT UNSIGNED  NOT NULL,
    student_id     INT UNSIGNED  NOT NULL,
    file_url       VARCHAR(2048) NOT NULL,
    submitted_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_submission UNIQUE (assignment_id, student_id),
    CONSTRAINT fk_submissions_assignment
        FOREIGN KEY (assignment_id) REFERENCES assignments(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_submissions_student
        FOREIGN KEY (student_id) REFERENCES users(id)
        ON DELETE CASCADE,
    INDEX idx_submissions_assignment (assignment_id),
    INDEX idx_submissions_student    (student_id)
);
