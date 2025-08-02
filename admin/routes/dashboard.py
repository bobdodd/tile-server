"""Admin dashboard routes."""

from flask import Blueprint, render_template, current_app
from pathlib import Path
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main admin dashboard."""
    # Get statistics
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

def get_dashboard_stats():
    """Calculate dashboard statistics."""
    tiles_dir = Path(current_app.config['TILES_DIR'])
    regions_dir = tiles_dir / 'regions'
    
    stats = {
        'total_regions': 0,
        'total_tiles': 0,
        'total_size_mb': 0,
        'regions': []
    }
    
    if regions_dir.exists():
        for region_dir in regions_dir.iterdir():
            if region_dir.is_dir():
                metadata_file = region_dir / 'metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        # Count tiles in region
                        tile_files = list(region_dir.glob('*.svg.gz'))
                        tile_count = len(tile_files)
                        
                        # Calculate size
                        total_size = sum(f.stat().st_size for f in tile_files)
                        size_mb = total_size / (1024 * 1024)
                        
                        region_stats = {
                            'name': metadata.get('display_name', region_dir.name),
                            'tile_count': tile_count,
                            'size_mb': size_mb,
                            'status': metadata.get('status', 'unknown')
                        }
                        
                        stats['regions'].append(region_stats)
                        stats['total_tiles'] += tile_count
                        stats['total_size_mb'] += size_mb
                        stats['total_regions'] += 1
                        
                    except Exception as e:
                        print(f"Error reading metadata for {region_dir}: {e}")
    
    return stats