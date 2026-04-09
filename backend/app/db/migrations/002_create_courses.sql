-- Migration 002: courses
-- Course catalogue. lecturer_id enforces the one-lecturer-per-course rule.
-- lecturer_id is SET NULL on user deletion so courses are not lost.

CREATE TABLE IF NOT EXISTS courses (
    id           INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(255)  NOT NULL,
    description  TEXT          NULL,
    lecturer_id  INT UNSIGNED  NULL,
    created_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                        ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_courses_lecturer
        FOREIGN KEY (lecturer_id) REFERENCES users(id)
        ON DELETE SET NULL,
    INDEX idx_courses_lecturer (lecturer_id)
);
