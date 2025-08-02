# SiteGround Deployment Guide

## Overview
SiteGround uses **Nginx** (not Apache) with Python support via their hosting platform. This guide covers deploying the tile server to SiteGround.

## SiteGround Specific Requirements

### 1. Python Environment
- SiteGround supports Python 3.8+ with their hosting
- They use their own Python app deployment system
- Virtual environments are managed through their control panel

### 2. Web Server
- **Nginx** (not Apache) - no .htaccess files
- Configuration is managed through SiteGround's control panel
- Static file serving is handled automatically

### 3. Application Structure
```
your-siteground-domain.com/
├── passenger_wsgi.py          # WSGI entry point
├── app.py                     # Flask application
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── admin/                     # Admin interface
├── api/                       # API endpoints
├── tile_generation/           # Generation modules
├── tiles/                     # Tile storage (served directly)
├── data/                      # Database and logs
└── deployment/
    ├── siteground-setup.md    # This file
    └── nginx.conf             # Reference (SiteGround manages)
```

## Deployment Steps

### Step 1: Prepare Files
1. Upload all files via SiteGround File Manager or FTP
2. Ensure directory structure matches above
3. Set proper permissions (755 for directories, 644 for files)

### Step 2: Python Environment Setup
1. Log into SiteGround control panel
2. Go to "Dev Tools" → "Python App"
3. Create new Python application:
   - **Python Version**: 3.8 or newer
   - **App Root**: `/` (or subdirectory if desired)
   - **App URL**: your domain or subdomain
   - **App Startup File**: `passenger_wsgi.py`

### Step 3: Install Dependencies
```bash
# SSH into your SiteGround account
ssh your-username@your-server.siteground.com

# Navigate to your app directory
cd ~/public_html/your-app

# Install requirements
pip install -r requirements.txt
```

### Step 4: Environment Configuration
Create a `.env` file in your app root:
```env
FLASK_CONFIG=production
SECRET_KEY=your-secret-key-here
SITE_URL=https://your-domain.com
```

### Step 5: Database Initialization
```bash
# Create database and tables
python -c "
from config import Config
from pathlib import Path
import sqlite3

# Ensure data directory exists
Path(Config.DATA_DIR).mkdir(exist_ok=True)

# Create database file
db_path = Path(Config.DATA_DIR) / 'database.db' 
conn = sqlite3.connect(db_path)
conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)')
conn.close()
print('Database initialized')
"
```

### Step 6: Static File Configuration
SiteGround automatically serves static files from these directories:
- `/tiles/` - Direct tile serving (high performance)
- `/admin/static/` - Admin interface assets
- Any other static directories

### Step 7: Test Deployment
1. Visit your domain to see the main page
2. Check `/admin/` for the admin interface
3. Test API endpoints at `/api/regions`
4. Verify tile serving at `/tiles/regions/toronto-downtown/`

## SiteGround-Specific Features

### 1. Built-in Caching
- SiteGround has built-in caching for static files
- Tile files (.svg.gz) are automatically cached
- No additional configuration needed

### 2. SSL/HTTPS
- Free SSL certificates through SiteGround
- Automatically configured for your domain
- Forces HTTPS redirect if enabled

### 3. Performance Optimization
- SiteGround's SuperCacher handles static file optimization
- Nginx serves tiles directly (bypasses Python)
- Built-in CDN available for global distribution

### 4. Monitoring
- Built-in resource usage monitoring
- Error logs available in control panel
- Python app metrics dashboard

## Configuration Notes

### Nginx (Managed by SiteGround)
SiteGround manages Nginx configuration automatically, but the effective config is similar to:
```nginx
# Tiles served directly by Nginx
location /tiles/ {
    root /home/username/public_html/your-app;
    expires 1d;
}

# Flask app served via Python
location / {
    proxy_pass http://python-app;
}
```

### File Permissions
```bash
# Set correct permissions
find . -type d -exec chmod 755 {} \;
find . -type f -exec chmod 644 {} \;
chmod +x passenger_wsgi.py
```

### Resource Limits
- Check SiteGround's Python resource limits
- Monitor memory usage during tile generation
- Consider upgrading plan if generating many tiles

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure all dependencies in requirements.txt
2. **Permission Denied**: Check file permissions (644/755)
3. **Database Errors**: Ensure data/ directory is writable
4. **Static Files Not Loading**: Check directory structure

### Logs
- Python app logs: SiteGround control panel → Python App → Logs  
- Error logs: Control panel → Statistics → Error Logs
- Access logs: Control panel → Statistics → Raw Access Logs

### Performance
- Monitor tile generation memory usage
- Use SiteGround's staging environment for testing
- Enable SiteGround's caching for production

## Migration from Development
1. Export any database data from development
2. Copy tile files to production `/tiles/` directory
3. Update configuration for production URLs
4. Test all endpoints before going live

## Maintenance
- Regular backups via SiteGround control panel
- Monitor disk usage (tile files can grow large)
- Update Python dependencies periodically
- Check SiteGround system updates