-- Migration 001: users
-- Stores all user accounts (admin, lecturer, student).
-- password_hash is nullable to support Google-only accounts.
-- google_id is nullable for username/password accounts.

CREATE TABLE IF NOT EXISTS users (
    id            INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)      NOT NULL UNIQUE,
    email         VARCHAR(255)     NOT NULL UNIQUE,
    password_hash VARCHAR(255)     NULL,
    role          ENUM('admin','lecturer','student') NOT NULL,
    google_id     VARCHAR(255)     NULL UNIQUE,
    created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                             ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role  (role),
    INDEX idx_users_email (email)
);
