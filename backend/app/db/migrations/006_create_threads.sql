-- Migration 006: threads
-- Top-level discussion topics inside a forum.
-- Each thread has a title and an opening body post.

CREATE TABLE IF NOT EXISTS threads (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    forum_id    INT UNSIGNED  NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    body        TEXT          NOT NULL,
    created_by  INT UNSIGNED  NOT NULL,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_threads_forum
        FOREIGN KEY (forum_id) REFERENCES forums(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_threads_creator
        FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_threads_forum (forum_id)
);
