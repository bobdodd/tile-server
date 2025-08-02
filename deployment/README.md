# Tile Generation Server - Complete Setup

## 🎯 Project Overview

This is a complete, standalone Flask tile generation server designed for SiteGround hosting. It generates and serves pre-rendered SVG tiles for accessible mapping applications.

### Features
- ✅ **Complete tile generation system** ported from original scripts
- ✅ **13 existing Toronto tiles** migrated and ready to serve
- ✅ **Flask admin interface** for tile management
- ✅ **RESTful API** for tile serving and missing tile reporting
- ✅ **SiteGround optimized** for Nginx + Python hosting
- ✅ **Canadian regions** pre-configured for September testing

## 📁 Server Structure

```
tile-server/                    # 🎯 Deploy this entire folder to SiteGround
├── app.py                     # Main Flask application
├── passenger_wsgi.py          # SiteGround WSGI entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── nginx.conf                 # Reference Nginx config
│
├── admin/                     # 🛠️ Admin Interface
│   ├── routes/               # Flask route handlers
│   ├── templates/            # HTML templates
│   └── static/              # CSS, JS, images
│
├── api/                      # 🔌 API Endpoints
│   ├── tiles.py             # Tile serving API
│   └── missing.py           # Missing tile reporting
│
├── tile_generation/          # ⚙️ Core Generation Engine
│   ├── builder.py           # Main tile builder (ported)
│   ├── osm_processor.py     # OSM data processing (ported)
│   └── feature_styles.py    # Feature styling definitions
│
├── tiles/                    # 🗺️ Generated Tiles Storage
│   ├── regions/
│   │   └── toronto-downtown/ # ✅ 13 tiles migrated from original
│   └── index.json           # Master tile index
│
├── data/                     # 💾 Database & Logs
│   ├── osm_cache/           # Cached OSM data
│   └── logs/                # Generation logs
│
└── deployment/              # 📋 Setup Documentation
    ├── siteground-setup.md  # Detailed deployment guide
    └── README.md            # This file
```

## 🚀 Quick Deployment to SiteGround

### 1. Upload Files
```bash
# Upload entire tile-server/ directory to SiteGround
# Via File Manager, FTP, or Git
```

### 2. Create Python App
1. SiteGround Control Panel → **Dev Tools** → **Python App**
2. **Create Application**:
   - Python Version: **3.8+**
   - App Root: **/** (or subdirectory)
   - App URL: **your-domain.com**
   - Startup File: **passenger_wsgi.py**

### 3. Install Dependencies
```bash
# SSH into SiteGround
ssh your-username@your-server.siteground.com
cd ~/public_html/your-app

# Install requirements
pip install -r requirements.txt
```

### 4. Test Deployment
- **Main Page**: `https://your-domain.com/`
- **Admin Interface**: `https://your-domain.com/admin/`  
- **API Endpoints**: `https://your-domain.com/api/regions`
- **Existing Tiles**: `https://your-domain.com/tiles/regions/toronto-downtown/`

## 🎛️ Access Points

| Interface | URL | Purpose |
|-----------|-----|---------|
| **Main Page** | `/` | Server overview and quick start |
| **Admin Dashboard** | `/admin/` | Tile and region management |
| **API Documentation** | `/api/regions` | Available regions and tile data |
| **Direct Tile Access** | `/tiles/regions/<region>/<tile>` | High-performance tile serving |

## 🗺️ Pre-Configured Regions

### Toronto Downtown (✅ Ready)
- **13 tiles migrated** from original system
- **Coverage**: Downtown Toronto core (43.63°N to 43.66°N, -79.41°W to -79.36°W)
- **Ready to serve** at `/tiles/regions/toronto-downtown/`

### Canadian Cities (⚙️ Configured for Generation)
- **Vancouver Downtown**
- **Calgary Downtown** 
- **Ottawa Downtown**
- **Montreal Downtown**

## 🔧 Usage Examples

### For Your Main ContextDescriptionApp
```javascript
// Update TileLoader to use new server
class TileLoader {
    constructor() {
        this.tileServerUrl = 'https://your-tile-server.com';
    }
    
    async loadTile(lat, lng) {
        const tileUrl = `${this.tileServerUrl}/tiles/regions/toronto-downtown/${lat}_${lng}.svg.gz`;
        
        try {
            const response = await fetch(tileUrl);
            if (!response.ok) {
                // Report missing tile to admin system
                this.reportMissingTile(lat, lng);
                return null;
            }
            return await this.decompressTile(response);
        } catch (error) {
            this.reportMissingTile(lat, lng);
            return null;
        }
    }
    
    async reportMissingTile(lat, lng) {
        try {
            await fetch(`${this.tileServerUrl}/api/missing-tile`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ lat, lng, timestamp: new Date().toISOString() })
            });
        } catch (error) {
            console.warn('Failed to report missing tile:', error);
        }
    }
}
```

### Admin Operations
```bash
# Generate new region (via admin interface or API)
curl -X POST https://your-tile-server.com/api/regions \
  -H "Content-Type: application/json" \
  -d '{
    "name": "vancouver-downtown",
    "bounds": {
      "north": 49.31, "south": 49.24,
      "east": -123.02, "west": -123.18
    }
  }'

# Check available regions
curl https://your-tile-server.com/api/regions

# List tiles in a region  
curl https://your-tile-server.com/api/region/toronto-downtown/tiles
```

## 📊 Monitoring & Maintenance

### SiteGround Resources
- **Memory Usage**: Monitor during tile generation
- **Disk Space**: Tiles can grow large (current: ~900KB for 13 tiles)
- **Python App Metrics**: Available in SiteGround control panel

### Logs & Debugging
- **Application Logs**: SiteGround Control Panel → Python App → Logs
- **Tile Generation**: Check `/data/logs/` directory
- **Missing Tiles**: Monitor API calls to `/api/missing-tile`

## 🎯 Next Steps for September Testing

### 1. Generate Canadian City Tiles
1. Access admin interface at `/admin/`
2. Create new regions for Vancouver, Calgary, Ottawa, Montreal
3. Generate tiles for each test city
4. Monitor generation progress and disk usage

### 2. Connect Your Main App
1. Update ContextDescriptionApp to point to new tile server
2. Test tile loading and missing tile reporting
3. Verify description generation with new tiles

### 3. Field Testing Preparation
1. Test server performance under load
2. Verify all Canadian cities have adequate coverage
3. Set up monitoring and alerting
4. Create backup/restore procedures

## 🆘 Support & Troubleshooting

### Common Issues
- **Import Errors**: Run `pip install -r requirements.txt`
- **Permission Denied**: Check file permissions (644/755)
- **Database Errors**: Ensure `/data/` directory is writable
- **Tile Not Found**: Check region name and tile coordinates

### Getting Help
- **Deployment Guide**: See `deployment/siteground-setup.md`
- **SiteGround Support**: For hosting-specific issues
- **Logs**: Check SiteGround control panel for detailed error logs

---

## ✅ Deployment Checklist

- [ ] Upload all files to SiteGround
- [ ] Create Python app in SiteGround control panel  
- [ ] Install dependencies via SSH
- [ ] Test main page loads
- [ ] Test admin interface at `/admin/`
- [ ] Test API endpoints at `/api/regions`
- [ ] Verify Toronto tiles serve at `/tiles/regions/toronto-downtown/`
- [ ] Generate tiles for additional Canadian cities
- [ ] Update main ContextDescriptionApp to use new server
- [ ] Test missing tile reporting functionality
- [ ] Set up monitoring and backups

**🎉 Your tile generation server is ready for September testing across Canada!**