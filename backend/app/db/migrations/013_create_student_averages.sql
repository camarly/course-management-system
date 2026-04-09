-- Migration 013: student_averages
-- Materialised average grade per student.
-- Updated asynchronously by the Celery recalculate_average task
-- after every grade write — never written directly by route handlers.

CREATE TABLE IF NOT EXISTS student_averages (
    id             INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    student_id     INT UNSIGNED  NOT NULL UNIQUE,
    average_grade  DECIMAL(5,2)  NOT NULL DEFAULT 0.00,
    last_updated   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                          ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_averages_student
        FOREIGN KEY (student_id) REFERENCES users(id)
        ON DELETE CASCADE
);
