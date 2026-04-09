-- Migration 004: calendar_events
-- Scheduled events scoped to a course.
-- event_date is used for the student date-filter query.

CREATE TABLE IF NOT EXISTS calendar_events (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    course_id   INT UNSIGNED  NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    description TEXT          NULL,
    event_date  DATE          NOT NULL,
    event_time  TIME          NULL,
    created_by  INT UNSIGNED  NOT NULL,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_events_course
        FOREIGN KEY (course_id) REFERENCES courses(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_events_creator
        FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_events_course_date (course_id, event_date)
);
