# Ziqsy Internal Admin System - Data Dictionary

## Database Schema Reference

### Core Tables

#### users
**Purpose**: Authentication and user management
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(120) | UNIQUE, NOT NULL | User login email |
| password_hash | VARCHAR(256) | NOT NULL | Hashed password for security |
| created_at | DATETIME | DEFAULT utcnow | Account creation timestamp |

**Sample Data**:
```
id: 1, email: "admin@ziqsy.com", created_at: "2025-06-17 10:30:00"
```

#### sections
**Purpose**: Organizational categories for pages
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique section identifier |
| name | VARCHAR(100) | NOT NULL | Section display name |
| created_at | DATETIME | DEFAULT utcnow | Section creation timestamp |

**Relationships**: One-to-many with pages

#### pages
**Purpose**: Individual content pages with different functionalities
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique page identifier |
| name | VARCHAR(100) | NOT NULL | Page display name |
| page_type | VARCHAR(50) | NOT NULL | Page functionality type |
| section_id | INTEGER | FOREIGN KEY | Parent section reference |
| table_name | VARCHAR(100) | NULL | Associated dynamic table name |
| config | TEXT | NULL | JSON configuration for page settings |
| created_at | DATETIME | DEFAULT utcnow | Page creation timestamp |

**Page Types**:
- `link_operations`: Category-based navigation with card display
- `list`: Flat table structure with CRUD operations
- `dataset`: Advanced data analysis with charts and AI assistant
- `repository`: File management with cloud folder integration

#### dynamic_table
**Purpose**: Metadata for dynamically created data tables
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique table identifier |
| table_name | VARCHAR(100) | UNIQUE, NOT NULL | Generated table name |
| page_id | INTEGER | FOREIGN KEY CASCADE | Associated page reference |
| columns_info | TEXT | NULL | JSON column definitions |
| created_at | DATETIME | DEFAULT utcnow | Table creation timestamp |

#### file_repository
**Purpose**: File and folder metadata for repository pages
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique file record identifier |
| page_id | INTEGER | FOREIGN KEY CASCADE | Associated page reference |
| file_path | VARCHAR(500) | NOT NULL | Full file path |
| file_name | VARCHAR(255) | NOT NULL | Display file name |
| description | TEXT | NULL | User-provided description |
| ai_description | TEXT | NULL | AI-generated description |
| user_notes | TEXT | NULL | User notes and comments |
| file_url | VARCHAR(500) | NULL | External file URL |
| tags | VARCHAR(500) | NULL | Comma-separated tags |
| is_folder | BOOLEAN | DEFAULT FALSE | True if record represents folder |
| created_at | DATETIME | DEFAULT utcnow | Record creation timestamp |

#### cloud_folder
**Purpose**: Cloud storage folder paths for repository pages
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Unique folder identifier |
| page_id | INTEGER | FOREIGN KEY CASCADE | Associated page reference |
| folder_path | VARCHAR(1000) | NOT NULL | Cloud folder path |
| folder_name | VARCHAR(255) | NOT NULL | Display folder name |
| created_at | DATETIME | DEFAULT utcnow | Folder association timestamp |

### Dynamic Tables

Dynamic tables are created programmatically based on uploaded CSV files. Their structure varies by content but follows these patterns:

**Naming Convention**: `page_{page_id}_data`

**Standard Columns**:
- `id`: INTEGER PRIMARY KEY (auto-increment)
- `created_at`: DATETIME DEFAULT utcnow
- `updated_at`: DATETIME DEFAULT utcnow

**Data Columns**: Based on CSV headers with sanitized names:
- Spaces replaced with underscores
- Special characters removed
- Lowercased for consistency

## Data Flow Patterns

### File Upload Process
1. User uploads CSV/Excel file via web interface
2. File saved to `/uploads/` directory temporarily
3. Pandas reads and validates file structure
4. Dynamic table created with sanitized column names
5. Data inserted into dynamic table
6. File metadata stored in `dynamic_table`
7. Temporary file removed

### AI Description Generation
1. User requests AI description for file/folder
2. System checks for OpenAI API key
3. API call made with file context
4. Response parsed and stored in `ai_description` field
5. Description displayed in repository interface

### Session Management
- Session data stored server-side
- `user_id` key identifies authenticated user
- Sessions persist across browser sessions
- Flash messages use Flask's session system

## Configuration Data

### Theme System
Stored in localStorage (client-side):
```json
{
  "selectedTheme": "dark|light|modern|oldschool|steel|gold"
}
```

### Page Configuration (JSON in pages.config)
```json
{
  "view_mode": "card|table",
  "items_per_page": 50,
  "sort_column": "column_name",
  "sort_direction": "asc|desc",
  "filter_categories": ["category1", "category2"]
}
```

## Error Handling Data

### Database Connection Fallback
When PostgreSQL is unavailable, system uses temporary in-memory storage:
- TempStorage class maintains session data
- Data structure mirrors database schema
- Automatically cleared on database reconnection

### File Processing Errors
Common error scenarios and data states:
- Invalid CSV format: Error logged, user notified
- Large file uploads: Progress tracking, chunked processing
- Duplicate uploads: Existing data preserved, user prompted

## Security Considerations

### Password Storage
- Passwords hashed using Werkzeug's generate_password_hash
- Default method used (currently pbkdf2:sha256)
- No plaintext passwords stored

### SQL Injection Prevention
- SQLAlchemy ORM used for all database queries
- Parameterized queries prevent injection attacks
- User input sanitized before dynamic table creation

### File Upload Security
- File type validation on upload
- Size limits enforced
- Temporary storage with automatic cleanup
- No executable file uploads permitted

## Performance Optimization

### Database Connections
- Connection pooling with 300-second recycle time
- Pre-ping enabled for connection health checks
- Automatic reconnection handling

### Data Loading
- Pagination for large datasets
- Lazy loading for related data
- Client-side caching for static content

## Backup and Recovery

### Data Persistence
- PostgreSQL handles transaction logging
- Dynamic tables included in standard backups
- File uploads stored in `/uploads/` directory
- Configuration data in database and localStorage

### Recovery Procedures
- Database schema recreation via SQLAlchemy models
- Dynamic table recreation from metadata
- File upload directory restoration required separately