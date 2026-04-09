-- Migration 012: grades
-- Numeric score recorded by a lecturer against a submission.
-- One grade per submission (unique constraint on submission_id).

CREATE TABLE IF NOT EXISTS grades (
    id             INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    submission_id  INT UNSIGNED  NOT NULL UNIQUE,
    graded_by      INT UNSIGNED  NOT NULL,
    score          DECIMAL(5,2)  NOT NULL,
    feedback       TEXT          NULL,
    graded_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_grades_submission
        FOREIGN KEY (submission_id) REFERENCES submissions(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_grades_lecturer
        FOREIGN KEY (graded_by) REFERENCES users(id),
    INDEX idx_grades_submission (submission_id)
);
