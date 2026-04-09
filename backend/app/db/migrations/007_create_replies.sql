-- Migration 007: replies
-- Posts inside a thread. Supports unlimited nesting via the self-referencing
-- parent_reply_id FK (NULL = direct reply to thread, non-NULL = reply to a reply).
-- Fetch the full tree using a recursive Common Table Expression (CTE).

CREATE TABLE IF NOT EXISTS replies (
    id              INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    thread_id       INT UNSIGNED  NOT NULL,
    parent_reply_id INT UNSIGNED  NULL,
    body            TEXT          NOT NULL,
    created_by      INT UNSIGNED  NOT NULL,
    created_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                           ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_replies_thread
        FOREIGN KEY (thread_id) REFERENCES threads(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_replies_parent
        FOREIGN KEY (parent_reply_id) REFERENCES replies(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_replies_creator
        FOREIGN KEY (created_by) REFERENCES users(id),
    INDEX idx_replies_thread (thread_id),
    INDEX idx_replies_parent (parent_reply_id)
);
