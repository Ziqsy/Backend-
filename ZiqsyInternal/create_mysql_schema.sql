-- Create database (run this in Hostinger phpMyAdmin or MySQL client)
CREATE DATABASE IF NOT EXISTS ziqsy_internal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE ziqsy_internal;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    sidebar_width INT DEFAULT 280,
    theme_preference VARCHAR(20) DEFAULT 'dark',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
);

-- Sections table
CREATE TABLE sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Pages table
CREATE TABLE pages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    page_type VARCHAR(50) NOT NULL,
    section_id INT NOT NULL,
    table_name VARCHAR(100) NULL,
    config TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (section_id) REFERENCES sections(id) ON DELETE CASCADE
);

-- Dynamic table metadata
CREATE TABLE dynamic_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL UNIQUE,
    page_id INT NOT NULL,
    columns_info TEXT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

-- File repository
CREATE TABLE file_repository (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    ai_description TEXT NULL,
    user_notes TEXT NULL,
    file_url VARCHAR(500) NULL,
    tags VARCHAR(500) NULL,
    is_folder BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

-- Cloud folder paths
CREATE TABLE cloud_folder (
    id INT AUTO_INCREMENT PRIMARY KEY,
    page_id INT NOT NULL,
    folder_path VARCHAR(1000) NOT NULL,
    folder_name VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
);

-- User invitations
CREATE TABLE user_invitation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    token VARCHAR(255) NOT NULL,
    created_by INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- Create indexes for better performance
CREATE INDEX idx_pages_section_id ON pages(section_id);
CREATE INDEX idx_dynamic_table_page_id ON dynamic_table(page_id);
CREATE INDEX idx_file_repository_page_id ON file_repository(page_id);
CREATE INDEX idx_cloud_folder_page_id ON cloud_folder(page_id);
CREATE INDEX idx_user_invitation_email ON user_invitation(email);


