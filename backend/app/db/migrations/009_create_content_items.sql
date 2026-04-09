-- Migration 009: content_items
-- Individual resources inside a content section.
-- item_type distinguishes links, uploaded files, and slide decks.

CREATE TABLE IF NOT EXISTS content_items (
    id          INT UNSIGNED  AUTO_INCREMENT PRIMARY KEY,
    section_id  INT UNSIGNED  NOT NULL,
    title       VARCHAR(255)  NOT NULL,
    item_type   ENUM('link','file','slide') NOT NULL,
    url         VARCHAR(2048) NOT NULL,
    position    INT UNSIGNED  NOT NULL DEFAULT 0,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_items_section
        FOREIGN KEY (section_id) REFERENCES content_sections(id)
        ON DELETE CASCADE,
    INDEX idx_items_section (section_id)
);
