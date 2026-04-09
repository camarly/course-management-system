-- Migration 008: content_sections
-- Named groupings of course material (e.g. "Week 1 Slides").
-- Ordered by the position column.

CREATE TABLE IF NOT EXISTS content_sections (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    course_id   INT UNSIGNED  NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    position    INT UNSIGNED  NOT NULL DEFAULT 0,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sections_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE,
    INDEX idx_sections_course (course_id)
);
