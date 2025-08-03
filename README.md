# Tile Generation Server - Local Mac Development

A Flask-based tile generation and management system that runs locally on your Mac and uploads tiles to SiteGround for static file serving.

## 🎯 Overview

This system:
- **Generates tiles locally** using your Mac's resources
- **Manages tiles** through a web-based admin interface  
- **Uploads tiles to SiteGround** via FTP for static serving
- **Serves tiles from SiteGround** to your mapping applications

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd tile-server
pip install -r requirements.txt
```

### 2. Configure SiteGround Upload
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your SiteGround FTP credentials
nano .env
```

Add your SiteGround details:
```env
SITEGROUND_HOST=yourdomain.com
SITEGROUND_USERNAME=your-ftp-username
SITEGROUND_PASSWORD=your-ftp-password
```

### 3. Run Local Server
```bash
python run_local.py
```

### 4. Access Admin Interface
- **Local Server**: http://127.0.0.1:5000
- **Admin Dashboard**: http://127.0.0.1:5000/admin/
- **API**: http://127.0.0.1:5000/api/regions

## 🛠️ Features

### Local Tile Generation
- Generate tiles for Canadian cities (Toronto, Vancouver, Calgary, Ottawa, Montreal)
- Process OpenStreetMap data into accessible SVG tiles
- Manage regions and tile coverage areas

### SiteGround Integration
- Upload tiles via FTP to your SiteGround hosting
- Test FTP connection from admin interface
- Sync all regions or upload individual regions
- Static file serving from SiteGround (fast, cached)

### Web Admin Interface
- Dashboard showing tile statistics
- Region management and tile generation
- Upload progress and status monitoring
- FTP connection testing

## 📁 Project Structure

```
tile-server/
├── run_local.py              # 🍎 Mac development server
├── .env.example              # Environment configuration template
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
│
├── admin/                    # 🛠️ Admin Interface
│   ├── routes/              # Flask routes
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── siteground_upload.py # SiteGround FTP upload
│
├── api/                      # 🔌 API Endpoints
│   ├── tiles.py             # Tile serving API
│   └── missing.py           # Missing tile reporting
│
├── tile_generation/          # ⚙️ Core Generation Engine
│   ├── builder.py           # Main tile builder
│   ├── osm_processor.py     # OSM data processing
│   └── feature_styles.py    # Feature styling
│
├── tiles/                    # 🗺️ Generated Tiles (local)
│   └── regions/
│       └── toronto-downtown/ # ✅ 13 existing tiles
│
└── data/                     # 💾 Database & Logs
    ├── database.db          # SQLite database
    ├── logs/                # Generation logs
    └── osm_cache/           # Cached OSM data
```

## 🔄 Workflow

### 1. Generate Tiles Locally
1. Open admin interface at http://127.0.0.1:5000/admin/
2. Select a Canadian region (Toronto, Vancouver, etc.)
3. Generate tiles using local Mac resources
4. Monitor progress in the admin interface

### 2. Upload to SiteGround
1. Click "Upload to SiteGround" for a region
2. Or use "Sync All Regions" to upload everything
3. Tiles are uploaded to `/public_html/tiles/regions/`
4. SiteGround serves them as static files

### 3. Use in Your Mapping App
Update your ContextDescriptionApp to load tiles from SiteGround:
```javascript
const tileUrl = `https://yourdomain.com/tiles/regions/toronto-downtown/${lat}_${lng}.svg.gz`;
```

## 🏗️ Canadian Regions (Pre-configured)

- **Toronto Downtown** ✅ (13 tiles ready)
- **Vancouver Downtown** ⚙️ (ready to generate)
- **Calgary Downtown** ⚙️ (ready to generate)
- **Ottawa Downtown** ⚙️ (ready to generate)
- **Montreal Downtown** ⚙️ (ready to generate)

## 🛡️ SiteGround Setup

### File Structure on SiteGround
```
public_html/
└── tiles/
    └── regions/
        ├── toronto-downtown/
        │   ├── 43.63_-79.41.svg.gz
        │   ├── 43.63_-79.40.svg.gz
        │   └── ...
        ├── vancouver-downtown/
        └── calgary-downtown/
```

### Nginx Configuration
SiteGround automatically serves these as static files with:
- Gzip compression support
- Caching headers
- High performance delivery

## 🔧 Development

### Environment Variables
```env
# Required for SiteGround upload
SITEGROUND_HOST=yourdomain.com
SITEGROUND_USERNAME=ftp-username
SITEGROUND_PASSWORD=ftp-password

# Optional Flask settings
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

### API Endpoints
- `GET /api/regions` - List available regions
- `GET /api/region/{name}/tiles` - List tiles in region
- `POST /api/missing-tile` - Report missing tile
- `GET /admin/test-connection` - Test SiteGround FTP

## 🚀 Deployment to Other Hosting

While designed for SiteGround, this can work with any hosting that supports:
- Static file serving
- FTP/SFTP upload
- Python/Flask (optional, for admin interface)

## 📈 Benefits

### 🍎 Local Development
- Use your Mac's full resources for tile generation
- No hosting resource limits during generation
- Familiar development environment

### 🌐 SiteGround Serving  
- Fast static file delivery
- Built-in caching and compression
- Reliable hosting infrastructure
- No Python hosting complications

### 🔄 Best of Both Worlds
- Generate heavy processing locally
- Serve lightweight files from hosting
- Easy management through web interface

## 🆘 Troubleshooting

### FTP Connection Issues
```bash
# Test FTP connection manually
ftp yourdomain.com
# Use your SiteGround FTP credentials
```

### Missing Dependencies
```bash
# Install missing packages
pip install -r requirements.txt

# For macOS-specific issues
brew install gdal  # For osmium/shapely
```

### Permission Issues
```bash
# Fix file permissions
chmod +x run_local.py
```

---

**🎉 Your tile generation system is ready for local Mac development with SiteGround serving!**