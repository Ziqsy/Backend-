# Ziqsy Internal Admin System - Troubleshooting Guide

## Quick Diagnostic Commands

### System Health Check
```bash
# Check if application is running
curl -s http://localhost:5000/health | jq .

# Check database connectivity
python -c "from app import db; print('DB OK' if db.session.execute('SELECT 1').scalar() else 'DB FAIL')"

# Check disk space
df -h
du -sh uploads/

# Check memory usage
free -h
ps aux --sort=-%mem | head -10
```

## Common Error Scenarios

### 1. Application Won't Start

#### Error: "ModuleNotFoundError: No module named 'flask'"
**Cause**: Missing dependencies
**Solution**:
```bash
pip install -r requirements.txt
# or
pip install flask flask-sqlalchemy gunicorn openai openpyxl pandas psycopg2-binary sqlalchemy werkzeug xlrd email-validator
```

#### Error: "sqlalchemy.exc.OperationalError: connection refused"
**Cause**: Database not accessible
**Diagnosis**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Test connection manually
psql $DATABASE_URL

# Check network connectivity
telnet db-host 5432
```
**Solutions**:
- Start PostgreSQL: `sudo systemctl start postgresql`
- Check DATABASE_URL format: `postgresql://user:pass@host:port/dbname`
- Verify firewall settings
- Check database user permissions

#### Error: "KeyError: 'SESSION_SECRET'"
**Cause**: Missing environment variable
**Solution**:
```bash
export SESSION_SECRET="your-secret-key-here"
# Add to ~/.bashrc or systemd service file for persistence
```

### 2. Authentication Issues

#### Error: "Invalid login credentials" with correct password
**Diagnosis**:
```python
# Check if user exists in database
python -c "
from app import app, db, User
with app.app_context():
    user = User.query.filter_by(email='admin@ziqsy.com').first()
    print('User exists:', user is not None)
    if user:
        print('Password check:', user.check_password('ziqsy2025'))
"
```
**Solutions**:
- Reset password in database
- Check password hashing method compatibility
- Verify database table structure

#### Error: Session expires immediately
**Cause**: SESSION_SECRET changing between requests
**Solution**:
- Set consistent SESSION_SECRET
- Check for application restarts
- Verify session storage configuration

### 3. File Upload Problems

#### Error: "413 Payload Too Large"
**Nginx Configuration**:
```nginx
http {
    client_max_body_size 100M;
}
```
**Flask Configuration**:
```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

#### Error: "Permission denied" on file save
**Diagnosis**:
```bash
# Check uploads directory permissions
ls -la uploads/
whoami
groups

# Check ownership
sudo chown -R www-data:www-data uploads/
sudo chmod 755 uploads/
```

#### Error: CSV parsing fails with "UnicodeDecodeError"
**Solution**:
```python
# In utils.py, modify CSV reading
try:
    df = pd.read_csv(filepath, encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv(filepath, encoding='latin-1')
```

### 4. Database Issues

#### Error: "Too many connections"
**Diagnosis**:
```sql
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
SELECT * FROM pg_stat_activity WHERE state != 'idle';
```
**Solutions**:
- Increase max_connections in PostgreSQL
- Optimize connection pooling
- Close unused connections

#### Error: "Relation does not exist"
**Diagnosis**:
```python
# Check if tables exist
python -c "
from app import app, db
with app.app_context():
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    print('Tables:', inspector.get_table_names())
"
```
**Solution**:
```python
# Recreate database schema
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

#### Error: Dynamic table creation fails
**Diagnosis**:
```python
# Check table naming and column sanitization
python -c "
from utils import sanitize_column_name
test_columns = ['User Name', 'Email Address', 'Date/Time']
print([sanitize_column_name(col) for col in test_columns])
"
```

### 5. AI Features Not Working

#### Error: "AI descriptions require OpenAI API key configuration"
**Diagnosis**:
```bash
echo $OPENAI_API_KEY
python -c "import os; print('Key set:', bool(os.environ.get('OPENAI_API_KEY')))"
```

#### Error: OpenAI API rate limit or timeout
**Diagnosis**:
```bash
# Test API directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4o","messages":[{"role":"user","content":"test"}],"max_tokens":5}' \
     https://api.openai.com/v1/chat/completions
```
**Solutions**:
- Check API key validity and permissions
- Verify billing account status
- Implement retry logic with exponential backoff

### 6. Performance Issues

#### Slow page loading
**Diagnosis**:
```bash
# Check database query performance
tail -f /var/log/postgresql/postgresql.log | grep "slow query"

# Monitor system resources
top
iostat 1 5
```
**Solutions**:
- Add database indexes for frequently queried columns
- Implement pagination for large datasets
- Optimize database queries
- Add caching layer

#### High memory usage
**Diagnosis**:
```bash
# Check memory usage by process
ps aux --sort=-%mem | head -10

# Monitor memory over time
watch -n 5 'free -h && echo "---" && ps aux --sort=-%mem | head -5'
```
**Solutions**:
```python
# Implement chunked processing for large files
def process_large_dataset(data, chunk_size=1000):
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        process_chunk(chunk)
        # Allow memory cleanup
        gc.collect()
```

### 7. Theme and UI Issues

#### Theme not persisting
**Browser Console Check**:
```javascript
console.log('Current theme:', localStorage.getItem('selectedTheme'));
console.log('Theme selector:', document.getElementById('themeSelector'));
```
**Solutions**:
- Clear browser localStorage
- Check JavaScript console for errors
- Verify theme CSS is loading properly

#### Sidebar not collapsing on mobile
**Diagnosis**:
```javascript
// Check mobile detection
console.log('Window width:', window.innerWidth);
console.log('Mobile overlay:', document.getElementById('mobileOverlay'));
```

## Debugging Workflows

### 1. Application Not Loading
```bash
# Step 1: Check if process is running
ps aux | grep gunicorn

# Step 2: Check logs
tail -f /var/log/gunicorn/error.log

# Step 3: Test manual startup
python main.py

# Step 4: Check dependencies
pip list | grep -E "(flask|sqlalchemy|psycopg2)"

# Step 5: Test database
python -c "from app import db; db.session.execute('SELECT 1')"
```

### 2. Data Not Displaying
```bash
# Step 1: Check if data exists
python -c "
from app import app, db, Section, Page
with app.app_context():
    print('Sections:', Section.query.count())
    print('Pages:', Page.query.count())
"

# Step 2: Check dynamic tables
python -c "
from app import app, db, DynamicTable
with app.app_context():
    tables = DynamicTable.query.all()
    for t in tables:
        print(f'Table: {t.table_name}, Page: {t.page_id}')
"

# Step 3: Test API endpoints
curl -s http://localhost:5000/api/page/1/data | jq .
```

### 3. File Upload Not Working
```bash
# Step 1: Check upload directory
ls -la uploads/
df -h uploads/

# Step 2: Test file permissions
touch uploads/test_file.txt
rm uploads/test_file.txt

# Step 3: Check file size limits
grep -r "client_max_body_size" /etc/nginx/
grep -r "MAX_CONTENT_LENGTH" .

# Step 4: Monitor upload process
tail -f /var/log/nginx/access.log | grep POST
```

## Log Analysis

### Application Logs
```bash
# Filter by error level
grep -i error /var/log/gunicorn/error.log

# Monitor real-time errors
tail -f /var/log/gunicorn/error.log | grep -i error

# Search for specific issues
grep -i "database\|connection\|timeout" /var/log/gunicorn/error.log
```

### Database Logs
```bash
# PostgreSQL slow queries
grep "slow query" /var/log/postgresql/postgresql.log

# Connection issues
grep -i "connection\|authentication" /var/log/postgresql/postgresql.log

# Lock problems
grep -i "lock\|deadlock" /var/log/postgresql/postgresql.log
```

### Web Server Logs
```bash
# Nginx error patterns
grep -E "(4[0-9]{2}|5[0-9]{2})" /var/log/nginx/access.log

# Large response times
awk '$NF > 1.0 {print $0}' /var/log/nginx/access.log

# Upload issues
grep -i "upload\|POST" /var/log/nginx/error.log
```

## Recovery Procedures

### 1. Database Recovery
```bash
# Create backup before any changes
pg_dump $DATABASE_URL > emergency_backup_$(date +%Y%m%d_%H%M).sql

# Drop and recreate schema (DESTRUCTIVE)
python -c "
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print('Schema recreated')
"

# Restore from backup
psql $DATABASE_URL < backup_file.sql
```

### 2. Application Recovery
```bash
# Reset to known good state
git stash
git checkout main
git pull origin main

# Reinstall dependencies
pip install -r requirements.txt

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

### 3. File System Recovery
```bash
# Recreate uploads directory
sudo mkdir -p uploads
sudo chown www-data:www-data uploads
sudo chmod 755 uploads

# Restore from backup
tar -xzf uploads_backup.tar.gz
```

## Prevention Strategies

### Monitoring Setup
```bash
# Create monitoring script
cat > monitor.sh << 'EOF'
#!/bin/bash
# Check application health
curl -s http://localhost:5000/health || echo "App down: $(date)"

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "High disk usage: ${DISK_USAGE}%"
fi

# Check memory
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.2f%%", $3*100/$2}')
echo "Memory usage: $MEMORY_USAGE"
EOF

chmod +x monitor.sh
```

### Automated Backups
```bash
# Daily backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump $DATABASE_URL | gzip > backup_${DATE}.sql.gz
tar -czf uploads_${DATE}.tar.gz uploads/
# Keep only last 7 days
find . -name "backup_*.sql.gz" -mtime +7 -delete
find . -name "uploads_*.tar.gz" -mtime +7 -delete
EOF

# Add to crontab
echo "0 2 * * * /path/to/backup.sh" | crontab -
```

### Health Checks
```python
# Add to routes.py
@app.route('/health')
def health_check():
    try:
        # Test database
        db.session.execute('SELECT 1')
        
        # Test disk space
        import shutil
        disk_usage = shutil.disk_usage('.')
        free_space_gb = disk_usage.free / (1024**3)
        
        # Test uploads directory
        uploads_exists = os.path.exists('uploads')
        
        return {
            'status': 'healthy',
            'database': 'connected',
            'disk_free_gb': round(free_space_gb, 2),
            'uploads_dir': 'exists' if uploads_exists else 'missing'
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500
```