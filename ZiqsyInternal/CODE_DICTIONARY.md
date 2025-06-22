# Ziqsy Internal Admin System - Code Dictionary

## Architecture Overview

### Backend Framework: Flask + SQLAlchemy
- **Main Application**: `main.py` (entry point)
- **App Configuration**: `app.py` (Flask app setup, database config)
- **Database Models**: `models.py` (SQLAlchemy ORM models)
- **Route Handlers**: `routes.py` (HTTP endpoints and business logic)
- **Utilities**: `utils.py` (data processing, file handling)
- **AI Services**: `ai_service.py` (OpenAI integration)
- **Fallback Storage**: `temp_storage.py` (in-memory storage for DB outages)

### Frontend Stack
- **Template Engine**: Jinja2 with Flask
- **CSS Framework**: Bootstrap 5 + custom themes
- **JavaScript**: Vanilla JS + Chart.js for visualization
- **Icons**: Font Awesome
- **Responsive Design**: Mobile-first approach with collapsible sidebar

## Core Components

### 1. Application Setup (`app.py`)

```python
# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,  # Prevent stale connections
    "pool_pre_ping": True,  # Health check before use
}
```

**Key Functions**:
- Database connection pooling
- ProxyFix middleware for proper header handling
- Session secret key from environment

### 2. Database Models (`models.py`)

#### Model Patterns
```python
class BaseModel:
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### Key Methods
- `set_password(password)`: Hash and store password
- `check_password(password)`: Verify password against hash
- `get_config()`: Parse JSON configuration
- `set_config(config_dict)`: Serialize and store configuration

### 3. Route Handlers (`routes.py`)

#### Authentication Routes
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Handles user authentication
    # Sets session['user_id'] on success
```

#### API Endpoints
```python
@app.route('/api/page/<int:page_id>/data')
def get_page_data(page_id):
    # Returns JSON data for dynamic tables
    # Handles pagination and filtering
```

#### File Upload Handler
```python
@app.route('/upload/<int:page_id>', methods=['POST'])
def upload_file(page_id):
    # Processes CSV/Excel uploads
    # Creates dynamic tables
    # Returns success/error status
```

### 4. Utility Functions (`utils.py`)

#### Dynamic Table Management
```python
def create_dynamic_table(table_name, columns):
    """
    Creates database table from CSV columns
    Sanitizes column names for SQL compatibility
    """
    
def sanitize_column_name(column_name):
    """
    Converts "User Name" -> "user_name"
    Removes special characters
    """
```

#### Data Processing
```python
def process_uploaded_file(filepath, page):
    """
    Handles multiple file formats:
    - CSV: pandas.read_csv()
    - Excel: pandas.read_excel()
    - JSON: pandas.read_json()
    """
```

### 5. AI Integration (`ai_service.py`)

```python
def generate_file_description(file_path, file_name, file_extension):
    """
    Uses OpenAI GPT-4o model
    Returns JSON-formatted description
    Handles API errors gracefully
    """
```

**API Configuration**:
- Model: `gpt-4o` (latest stable)
- Response format: JSON object
- Token limit: 150 tokens
- Timeout handling included

## Frontend Architecture

### 1. Theme System

#### CSS Variables Pattern
```css
:root {
    --primary-bg: #1a202c;
    --accent-color: #14b8a6;
    --text-color: #ffffff;
}

[data-theme="light"] {
    --primary-bg: #ffffff;
    --accent-color: #3b82f6;
    --text-color: #1f2937;
}
```

#### Theme Switching
```javascript
function changeTheme() {
    const selectedTheme = themeSelector.value;
    document.body.setAttribute('data-theme', selectedTheme);
    localStorage.setItem('selectedTheme', selectedTheme);
}
```

### 2. Sidebar Navigation

#### Collapsible Functionality
```javascript
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('collapsed');
}
```

#### Mobile Responsiveness
```css
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .sidebar.mobile-open {
        transform: translateX(0);
    }
}
```

### 3. Data Visualization

#### Chart.js Integration
```javascript
function createChart(type, data, labels) {
    const ctx = document.getElementById('dataChart').getContext('2d');
    
    new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: getThemeColors()
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
```

## Error Handling Patterns

### 1. Database Connection Errors

```python
try:
    # Database operation
    db.session.commit()
except Exception as e:
    app.logger.error(f"Database error: {e}")
    db.session.rollback()
    # Fallback to temp storage
    temp_storage.add_section(name)
```

### 2. File Processing Errors

```python
def safe_file_process(filepath, page):
    try:
        df = pd.read_csv(filepath)
        return process_dataframe(df, page)
    except pd.errors.EmptyDataError:
        return {'error': 'File is empty'}
    except pd.errors.ParserError:
        return {'error': 'Invalid file format'}
    except Exception as e:
        app.logger.error(f"File processing error: {e}")
        return {'error': 'Processing failed'}
```

### 3. AI Service Errors

```python
def generate_description_with_fallback(file_info):
    if not openai:
        return "AI descriptions require OpenAI API key configuration"
    
    try:
        response = openai.chat.completions.create(...)
        return parse_response(response)
    except openai.RateLimitError:
        return "Rate limit exceeded, try again later"
    except Exception as e:
        return f"Unable to generate description: {str(e)}"
```

## Security Implementation

### 1. Authentication
```python
@app.before_request
def require_login():
    if request.endpoint in ['login', 'static']:
        return
    if 'user_id' not in session:
        return redirect(url_for('login'))
```

### 2. SQL Injection Prevention
```python
# Safe: Using SQLAlchemy ORM
user = User.query.filter_by(email=email).first()

# Unsafe: Raw SQL with user input
# cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

### 3. File Upload Security
```python
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls', '.json', '.md'}

def allowed_file(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS

def secure_filename_custom(filename):
    # Remove path separators and dangerous characters
    filename = secure_filename(filename)
    return filename[:255]  # Limit length
```

## Performance Optimization

### 1. Database Queries
```python
# Efficient: Eager loading
sections = Section.query.options(
    joinedload(Section.pages)
).all()

# Inefficient: N+1 queries
# sections = Section.query.all()
# for section in sections:
#     pages = section.pages  # Triggers new query each time
```

### 2. Frontend Optimization
```javascript
// Debounced search to reduce API calls
const debouncedSearch = debounce(function(searchTerm) {
    fetch(`/api/search?q=${searchTerm}`)
        .then(response => response.json())
        .then(updateResults);
}, 300);
```

### 3. Caching Strategy
```python
# Client-side caching for static data
def get_cached_data(key, fetch_function, ttl=300):
    cached = cache.get(key)
    if cached and not expired(cached, ttl):
        return cached['data']
    
    data = fetch_function()
    cache.set(key, {'data': data, 'timestamp': time.time()})
    return data
```

## Deployment Configuration

### 1. Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
SESSION_SECRET=your-secret-key-here
OPENAI_API_KEY=your-openai-api-key
```

### 2. Gunicorn Configuration
```python
# main.py - Production entry point
from app import app

if __name__ == '__main__':
    app.run(debug=False)
```

```bash
# Production command
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### 3. Static File Serving
```python
# Development: Flask serves static files
app.static_folder = 'static'

# Production: Use nginx or CDN for static files
# Configure reverse proxy for Flask app
```

## Testing and Debugging

### 1. Logging Configuration
```python
import logging

if app.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
```

### 2. Debug Helpers
```python
def debug_sql_queries():
    """Enable SQL query logging"""
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def debug_routes():
    """Print all registered routes"""
    for rule in app.url_map.iter_rules():
        print(f"{rule.rule} -> {rule.endpoint}")
```

### 3. Error Tracking
```python
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    db.session.rollback()
    return render_template('error.html'), 500
```

## Common Issues and Solutions

### 1. Database Connection Lost
**Symptom**: "Lost connection to MySQL server"
**Solution**: 
```python
# Implemented in app.py
"pool_recycle": 300,  # Refresh connections every 5 minutes
"pool_pre_ping": True  # Test connection before use
```

### 2. Large File Upload Timeout
**Symptom**: Request timeout on large CSV files
**Solution**:
```python
# Chunked processing for large files
def process_large_file(filepath, chunk_size=10000):
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        process_chunk(chunk)
```

### 3. Memory Usage on Dynamic Tables
**Symptom**: High memory usage with multiple large datasets
**Solution**:
```python
# Implement pagination and lazy loading
def get_paginated_data(table_name, page=1, per_page=100):
    offset = (page - 1) * per_page
    query = f"SELECT * FROM {table_name} LIMIT {per_page} OFFSET {offset}"
    return db.session.execute(text(query)).fetchall()
```

## Maintenance Tasks

### 1. Database Cleanup
```python
def cleanup_temp_files():
    """Remove files older than 1 hour from uploads directory"""
    cutoff = datetime.utcnow() - timedelta(hours=1)
    for file in os.listdir('uploads'):
        file_path = os.path.join('uploads', file)
        if os.path.getctime(file_path) < cutoff.timestamp():
            os.remove(file_path)
```

### 2. Log Rotation
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'app.log', 
    maxBytes=10000000,  # 10MB
    backupCount=5
)
app.logger.addHandler(handler)
```

### 3. Health Check Endpoint
```python
@app.route('/health')
def health_check():
    try:
        db.session.execute(text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```