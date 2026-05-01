-- Migration 001: users
-- Stores all user accounts (admin, lecturer, student).
-- Authentication: username + bcrypt password hash + JWT.

CREATE TABLE IF NOT EXISTS users (
    id            INT UNSIGNED     AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)      NOT NULL UNIQUE,
    email         VARCHAR(255)     NOT NULL UNIQUE,
    password_hash VARCHAR(255)     NOT NULL,
    role          ENUM('admin','lecturer','student') NOT NULL,
    created_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP        NOT NULL DEFAULT CURRENT_TIMESTAMP
                                             ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role  (role),
    INDEX idx_users_email (email)
);
