# PostgreSQL to MySQL Migration Guide for Hostinger

## Overview

This guide provides step-by-step instructions to migrate your Ziqsy Internal Admin System from PostgreSQL to MySQL for deployment on Hostinger.

## Phase 1: Prerequisites and Preparation

### 1.1 Hostinger Setup
1. **Create MySQL Database in Hostinger**
   - Login to Hostinger hPanel
   - Go to "Databases" → "MySQL Databases"
   - Create new database (e.g., `ziqsy_internal`)
   - Create database user with full privileges
   - Note down: database name, username, password, and host

### 1.2 Required Tools
Install MySQL connector for Python:
```bash
pip install PyMySQL mysqlclient
```

### 1.3 Export Current PostgreSQL Data
```bash
# Export schema and data
pg_dump postgresql://username:password@host:port/database_name > ziqsy_backup.sql

# Export data only (CSV format for easier conversion)
psql -d your_database_url -c "\COPY users TO 'users.csv' WITH CSV HEADER;"
psql -d your_database_url -c "\COPY sections TO 'sections.csv' WITH CSV HEADER;"
psql -d your_database_url -c "\COPY pages TO 'pages.csv' WITH CSV HEADER;"
psql -d your_database_url -c "\COPY dynamic_table TO 'dynamic_table.csv' WITH CSV HEADER;"
psql -d your_database_url -c "\COPY file_repository TO 'file_repository.csv' WITH CSV HEADER;"
psql -d your_database_url -c "\COPY cloud_folder TO 'cloud_folder.csv' WITH CSV HEADER;"
psql -d your_database_url -c "\COPY user_invitation TO 'user_invitation.csv' WITH CSV HEADER;"
```

## Phase 2: Code Modifications

### 2.1 Update Dependencies
Replace in your requirements file:
```
# Remove
psycopg2-binary

# Add
PyMySQL==1.1.0
mysqlclient==2.2.4
```

### 2.2 Update Database Configuration
Modify `app.py`:
```python
# Replace PostgreSQL URL format
# OLD: postgresql://user:pass@host/db
# NEW: mysql://user:pass@host/db

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
# Ensure DATABASE_URL format: mysql://username:password@hostname/database_name
```

### 2.3 Model Modifications for MySQL Compatibility

Create `mysql_models.py` with MySQL-compatible schema:
```python
from app import db
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased for MySQL
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sidebar_width = db.Column(db.Integer, default=280)
    theme_preference = db.Column(db.String(20), default='dark')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_domain_allowed(self):
        allowed_domains = ['@ziqsy.com', '@technicologyltd.com']
        return any(self.email.endswith(domain) for domain in allowed_domains)

class Section(db.Model):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to pages
    pages = db.relationship('Page', backref='section', lazy=True, cascade='all, delete-orphan')

class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    page_type = db.Column(db.String(50), nullable=False)  # link_operations, list, dataset, repository
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    table_name = db.Column(db.String(100), nullable=True)  # For dynamic tables
    config = db.Column(db.Text, nullable=True)  # JSON config for page-specific settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_config(self):
        if self.config:
            return json.loads(self.config)
        return {}

    def set_config(self, config_dict):
        self.config = json.dumps(config_dict)

class DynamicTable(db.Model):
    __tablename__ = 'dynamic_table'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_name = db.Column(db.String(100), unique=True, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    columns_info = db.Column(db.Text, nullable=True)  # JSON info about columns
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_columns_info(self):
        if self.columns_info:
            return json.loads(self.columns_info)
        return {}

    def set_columns_info(self, columns_dict):
        self.columns_info = json.dumps(columns_dict)

class FileRepository(db.Model):
    __tablename__ = 'file_repository'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    ai_description = db.Column(db.Text, nullable=True)  # AI-generated description
    user_notes = db.Column(db.Text, nullable=True)  # User notes about the file/folder
    file_url = db.Column(db.String(500), nullable=True)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    is_folder = db.Column(db.Boolean, default=False)  # True if this is a folder
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CloudFolder(db.Model):
    __tablename__ = 'cloud_folder'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False)
    folder_path = db.Column(db.String(1000), nullable=False)
    folder_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserInvitation(db.Model):
    __tablename__ = 'user_invitation'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(255), nullable=False)  # Reduced for MySQL
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
```

## Phase 3: MySQL Schema Creation

### 3.1 Create MySQL Schema Script
Create `create_mysql_schema.sql`:

```sql
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
```

## Phase 4: Data Migration Process

### 4.1 Convert PostgreSQL Data to MySQL Format

Create `migrate_data.py`:
```python
import csv
import mysql.connector
from datetime import datetime
import os

# MySQL connection configuration
MYSQL_CONFIG = {
    'host': 'your-hostinger-mysql-host',
    'user': 'your-mysql-username',
    'password': 'your-mysql-password',
    'database': 'ziqsy_internal',
    'charset': 'utf8mb4'
}

def connect_mysql():
    return mysql.connector.connect(**MYSQL_CONFIG)

def migrate_table_data(csv_file, table_name, column_mapping):
    """Migrate data from CSV to MySQL table"""
    conn = connect_mysql()
    cursor = conn.cursor()
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Convert data types for MySQL
            converted_row = {}
            for csv_col, mysql_col in column_mapping.items():
                value = row.get(csv_col, '')
                
                # Handle boolean conversion
                if value in ['t', 'true', 'True', '1']:
                    converted_row[mysql_col] = True
                elif value in ['f', 'false', 'False', '0']:
                    converted_row[mysql_col] = False
                elif value == '' or value == 'NULL':
                    converted_row[mysql_col] = None
                else:
                    converted_row[mysql_col] = value
            
            # Build INSERT query
            columns = list(converted_row.keys())
            placeholders = ', '.join(['%s'] * len(columns))
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            try:
                cursor.execute(query, list(converted_row.values()))
            except Exception as e:
                print(f"Error inserting row into {table_name}: {e}")
                print(f"Row data: {converted_row}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Migrated data to {table_name}")

# Define column mappings (PostgreSQL -> MySQL)
COLUMN_MAPPINGS = {
    'users': {
        'id': 'id',
        'email': 'email',
        'password_hash': 'password_hash',
        'is_admin': 'is_admin',
        'is_active': 'is_active',
        'sidebar_width': 'sidebar_width',
        'theme_preference': 'theme_preference',
        'created_at': 'created_at',
        'last_login': 'last_login'
    },
    'sections': {
        'id': 'id',
        'name': 'name',
        'created_at': 'created_at'
    },
    'pages': {
        'id': 'id',
        'name': 'name',
        'page_type': 'page_type',
        'section_id': 'section_id',
        'table_name': 'table_name',
        'config': 'config',
        'created_at': 'created_at'
    }
    # Add other tables as needed
}

if __name__ == "__main__":
    # Migrate each table
    for table_name, mapping in COLUMN_MAPPINGS.items():
        csv_file = f"{table_name}.csv"
        if os.path.exists(csv_file):
            migrate_table_data(csv_file, table_name, mapping)
        else:
            print(f"CSV file {csv_file} not found, skipping {table_name}")
```

### 4.2 Create Admin User for MySQL
Create `create_admin_user.py`:
```python
import mysql.connector
from werkzeug.security import generate_password_hash

MYSQL_CONFIG = {
    'host': 'your-hostinger-mysql-host',
    'user': 'your-mysql-username',
    'password': 'your-mysql-password',
    'database': 'ziqsy_internal',
    'charset': 'utf8mb4'
}

def create_admin_user():
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()
    
    # Check if admin user exists
    cursor.execute("SELECT id FROM users WHERE email = %s", ('admin@ziqsy.com',))
    if cursor.fetchone():
        print("Admin user already exists")
        return
    
    # Create admin user
    password_hash = generate_password_hash('ziqsy2025')
    query = """
    INSERT INTO users (email, password_hash, is_admin, is_active, sidebar_width, theme_preference)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = ('admin@ziqsy.com', password_hash, True, True, 280, 'dark')
    
    cursor.execute(query, values)
    conn.commit()
    
    print("Admin user created successfully")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    create_admin_user()
```

## Phase 5: Environment Configuration

### 5.1 Update Environment Variables
In your Hostinger hosting environment, set:
```
DATABASE_URL=mysql://username:password@hostname/database_name
SESSION_SECRET=your-secure-session-secret
OPENAI_API_KEY=your-openai-key-if-needed
```

### 5.2 Update requirements.txt
```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
gunicorn==21.2.0
PyMySQL==1.1.0
mysqlclient==2.2.4
pandas==2.1.4
openpyxl==3.1.2
xlrd==2.0.1
email-validator==2.1.0
Werkzeug==3.0.1
SQLAlchemy==2.0.23
markdown==3.7
pdfkit==1.0.0
```

## Phase 6: Testing and Deployment

### 6.1 Local Testing with MySQL
1. Set up local MySQL instance
2. Run migration scripts
3. Test application functionality
4. Verify all features work correctly

### 6.2 Hostinger Deployment Steps
1. **Upload Files**
   - Upload your application files to Hostinger
   - Ensure all Python dependencies are installed

2. **Database Setup**
   - Run the MySQL schema creation script in phpMyAdmin
   - Execute data migration scripts
   - Create admin user

3. **Configuration**
   - Set environment variables in Hostinger control panel
   - Configure Python app settings

4. **Testing**
   - Test login functionality
   - Verify all page types work
   - Check file upload/download
   - Test admin user management

## Phase 7: Post-Migration Cleanup

### 7.1 Verify Data Integrity
```sql
-- Check record counts match
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM sections;
SELECT COUNT(*) FROM pages;
-- Compare with PostgreSQL counts
```

### 7.2 Performance Optimization
```sql
-- Analyze tables for better performance
ANALYZE TABLE users, sections, pages, dynamic_table, file_repository;

-- Check indexes are being used
EXPLAIN SELECT * FROM pages WHERE section_id = 1;
```

## Troubleshooting Common Issues

### Issue 1: Character Encoding Problems
**Solution**: Ensure UTF-8 encoding:
```sql
ALTER DATABASE ziqsy_internal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Issue 2: DateTime Format Differences
**Solution**: Use MySQL-compatible datetime format in Python:
```python
# Use this format for MySQL
datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```

### Issue 3: Boolean Field Issues
**Solution**: MySQL handles booleans as TINYINT:
```python
# In your models, explicitly handle boolean conversion
is_active = db.Column(db.Boolean, default=False)
```

### Issue 4: Auto-increment Issues
**Solution**: Reset auto-increment if needed:
```sql
ALTER TABLE users AUTO_INCREMENT = 1;
```

## Final Checklist

- [ ] MySQL database created in Hostinger
- [ ] Schema created successfully
- [ ] Data migrated from PostgreSQL
- [ ] Admin user created
- [ ] Environment variables configured
- [ ] Application code updated for MySQL
- [ ] All dependencies installed
- [ ] Application tested locally with MySQL
- [ ] Application deployed to Hostinger
- [ ] All features verified working
- [ ] Performance optimized

## Support Commands

### Backup MySQL Database
```bash
mysqldump -h hostname -u username -p database_name > backup.sql
```

### Restore MySQL Database
```bash
mysql -h hostname -u username -p database_name < backup.sql
```

This comprehensive guide should help you successfully migrate from PostgreSQL to MySQL for your Hostinger deployment.