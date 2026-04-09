-- Migration 005: forums
-- Discussion boards scoped to a course.
-- A course can have multiple forums.

CREATE TABLE IF NOT EXISTS forums (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    course_id   INT UNSIGNED  NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    description TEXT          NULL,
    created_by  INT UNSIGNED  NOT NULL,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_forums_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_forums_creator
        FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_forums_course (course_id)
);
