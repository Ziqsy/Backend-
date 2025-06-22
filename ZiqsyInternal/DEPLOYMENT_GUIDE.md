# Ziqsy Internal Admin System - Deployment Guide

## Quick Deployment Checklist

### Prerequisites
- [ ] Python 3.11+ installed
- [ ] PostgreSQL database available
- [ ] Required environment variables set
- [ ] OpenAI API key (optional, for AI features)

### Environment Variables
```bash
DATABASE_URL=postgresql://username:password@host:port/database_name
SESSION_SECRET=your-secure-random-secret-key-here
OPENAI_API_KEY=sk-your-openai-api-key-here  # Optional
```

### Installation Steps
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run database setup: `python -c "from app import app, db; app.app_context().push(); db.create_all()"`
5. Start application: `gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app`

## Production Deployment

### Server Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 20GB minimum (depends on file uploads)
- **Network**: HTTPS enabled, port 5000 accessible

### Database Configuration
```sql
-- Create database and user
CREATE DATABASE ziqsy_internal;
CREATE USER ziqsy_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ziqsy_internal TO ziqsy_user;
```

### Gunicorn Production Config
```bash
# recommended production command
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --worker-class sync \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --timeout 300 \
  --keepalive 2 \
  --reuse-port \
  main:app
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    client_max_body_size 100M;  # For file uploads
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## Health Monitoring

### Built-in Health Check
```bash
curl http://localhost:5000/health
# Expected response: {"status": "healthy", "database": "connected"}
```

### Log Monitoring
- Application logs: Check gunicorn output
- Database logs: Monitor PostgreSQL logs
- File uploads: Monitor `/uploads/` directory size

### Performance Metrics
- Database connection pool usage
- Response times for heavy operations (file uploads, AI calls)
- Memory usage during large dataset processing

## Backup Strategy

### Database Backup
```bash
# Daily backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql

# Restoration
psql $DATABASE_URL < backup_20250618.sql
```

### File Backup
```bash
# Backup uploads directory
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/

# Include in system backup schedule
```

### Configuration Backup
- Environment variables configuration
- Nginx/Apache configuration files
- SSL certificates

## Security Configuration

### HTTPS Setup
```bash
# Using certbot for Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

### Firewall Configuration
```bash
# UFW example
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Database Security
- Use strong passwords
- Limit database user privileges
- Enable SSL connections
- Regular security updates

## Scaling Considerations

### Horizontal Scaling
- Load balancer configuration
- Session store (Redis recommended)
- Shared file storage (NFS/S3)

### Database Scaling
- Read replicas for heavy datasets
- Connection pooling optimization
- Query performance monitoring

### CDN Integration
- Static asset delivery
- File upload handling
- Geographic distribution

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
**Symptoms**: "Lost connection to MySQL server", "Connection refused"
**Solutions**:
- Check DATABASE_URL format
- Verify database server is running
- Check network connectivity
- Review connection pool settings

#### 2. File Upload Failures
**Symptoms**: Upload timeouts, "413 Payload Too Large"
**Solutions**:
- Increase nginx `client_max_body_size`
- Adjust gunicorn timeout settings
- Check disk space in uploads directory
- Verify file permissions

#### 3. AI Features Not Working
**Symptoms**: "AI descriptions require OpenAI API key", timeout errors
**Solutions**:
- Verify OPENAI_API_KEY is set correctly
- Check API key permissions and usage limits
- Test API connectivity: `curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models`

#### 4. Memory Issues
**Symptoms**: High memory usage, OOM kills
**Solutions**:
- Implement pagination for large datasets
- Optimize database queries
- Increase server memory
- Add monitoring for memory leaks

### Debugging Commands

```bash
# Check application status
ps aux | grep gunicorn

# View recent logs
tail -f /var/log/gunicorn/error.log

# Database connection test
python -c "from app import db; print(db.session.execute('SELECT 1').scalar())"

# Check environment variables
env | grep -E "(DATABASE_URL|SESSION_SECRET|OPENAI)"

# Disk space check
df -h
du -sh uploads/
```

## Maintenance Tasks

### Regular Maintenance (Weekly)
- [ ] Check application logs for errors
- [ ] Verify database backup integrity
- [ ] Monitor disk space usage
- [ ] Review performance metrics

### Monthly Maintenance
- [ ] Update dependencies (review changelog first)
- [ ] Rotate log files
- [ ] Clean old uploaded files
- [ ] Database optimization (VACUUM, ANALYZE)

### Security Updates
- [ ] Operating system patches
- [ ] Python security updates
- [ ] Database security patches
- [ ] SSL certificate renewal

## Performance Optimization

### Database Optimization
```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_pages_section_id ON pages(section_id);
CREATE INDEX idx_file_repository_page_id ON file_repository(page_id);
CREATE INDEX idx_dynamic_table_page_id ON dynamic_table(page_id);
```

### Application Optimization
- Enable gzip compression in nginx
- Implement Redis caching for frequent queries
- Optimize static asset delivery
- Use database connection pooling

### Monitoring Setup
```python
# Add to app.py for monitoring
import time
from flask import g

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request(response):
    duration = time.time() - g.start_time
    app.logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
    return response
```

## Disaster Recovery

### Recovery Procedures
1. **Database Corruption**:
   - Restore from latest backup
   - Verify data integrity
   - Update application configuration

2. **File System Issues**:
   - Restore uploads directory
   - Check file permissions
   - Verify application access

3. **Complete System Failure**:
   - Deploy on new server
   - Restore database from backup
   - Restore uploaded files
   - Update DNS if necessary

### Recovery Testing
- Monthly backup restoration tests
- Verify all functionality after restoration
- Document recovery time objectives

## Support and Maintenance

### Log Locations
- Application: `/var/log/gunicorn/`
- Database: PostgreSQL log directory
- Web server: `/var/log/nginx/`

### Configuration Files
- Application: `app.py`, environment variables
- Database: PostgreSQL configuration
- Web server: Nginx/Apache configuration

### Contact Information
- System Administrator: [contact details]
- Database Administrator: [contact details]
- Development Team: [contact details]

### Emergency Procedures
1. Check system health endpoint
2. Review recent logs for errors
3. Verify database connectivity
4. Check disk space and memory usage
5. Contact appropriate team member

## Version Control and Deployment

### Git Workflow
```bash
# Production deployment
git checkout main
git pull origin main
pip install -r requirements.txt
# Run database migrations if any
python -c "from app import db; db.create_all()"
# Restart application server
sudo systemctl restart gunicorn
```

### Environment Management
- Development: Local PostgreSQL, debug mode enabled
- Staging: Production-like environment for testing
- Production: Full monitoring, backups, security enabled

### Rollback Procedures
```bash
# Quick rollback to previous version
git checkout [previous-commit-hash]
sudo systemctl restart gunicorn

# Database rollback (if schema changes)
psql $DATABASE_URL < backup_before_deployment.sql
```