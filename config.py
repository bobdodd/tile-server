"""Configuration settings for the tile generation server."""
import os
from pathlib import Path

class Config:
    """Base configuration class."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///data/database.db'
    
    # Directory paths
    BASE_DIR = Path(__file__).parent
    TILES_DIR = BASE_DIR / 'tiles'
    DATA_DIR = BASE_DIR / 'data'
    
    # OSM API settings
    OSM_API_BASE = 'https://overpass-api.de/api/interpreter'
    OSM_CACHE_HOURS = 24  # Cache OSM data for 24 hours
    OSM_TIMEOUT = 300  # 5 minutes timeout for OSM queries
    
    # Tile generation settings
    TILE_SIZE_DEGREES = 0.01  # 0.01 degrees per tile (roughly 1km)
    SVG_SIZE = 1000  # SVG viewport size
    
    # SiteGround specific
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:5000')
    
    # Pre-configured Canadian regions for September testing
    PRESET_REGIONS = {
        'toronto-downtown': {
            'name': 'Toronto Downtown',
            'description': 'Downtown Toronto core area for testing',
            'bounds': {
                'north': 43.68,
                'south': 43.62, 
                'east': -79.34,
                'west': -79.40
            }
        },
        'toronto-gta': {
            'name': 'Greater Toronto Area',
            'description': 'Extended GTA coverage',
            'bounds': {
                'north': 43.85,
                'south': 43.60,
                'east': -79.10,
                'west': -79.65
            }
        },
        'vancouver-downtown': {
            'name': 'Vancouver Downtown',
            'description': 'Downtown Vancouver core area',
            'bounds': {
                'north': 49.31,
                'south': 49.24,
                'east': -123.02,
                'west': -123.18
            }
        },
        'calgary-downtown': {
            'name': 'Calgary Downtown', 
            'description': 'Downtown Calgary core area',
            'bounds': {
                'north': 51.15,
                'south': 51.00,
                'east': -113.90,
                'west': -114.20
            }
        },
        'ottawa-downtown': {
            'name': 'Ottawa Downtown',
            'description': 'Downtown Ottawa core area',
            'bounds': {
                'north': 45.50,
                'south': 45.35,
                'east': -75.60,
                'west': -75.80
            }
        },
        'montreal-downtown': {
            'name': 'Montreal Downtown',
            'description': 'Downtown Montreal core area', 
            'bounds': {
                'north': 45.58,
                'south': 45.45,
                'east': -73.50,
                'west': -73.70
            }
        }
    }

class DevelopmentConfig(Config):
    """Local Mac development configuration."""
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000
    
    # SiteGround upload settings (set via environment variables)
    SITEGROUND_HOST = os.environ.get('SITEGROUND_HOST', '')
    SITEGROUND_USERNAME = os.environ.get('SITEGROUND_USERNAME', '')
    SITEGROUND_PASSWORD = os.environ.get('SITEGROUND_PASSWORD', '')
    SITEGROUND_TILES_PATH = '/public_html/tiles/'
    
class ProductionConfig(Config):
    """Production configuration for SiteGround."""
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    def __init__(self):
        # Only validate SECRET_KEY when actually using production config
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production")

# Configuration factory
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}