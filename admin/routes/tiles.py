"""Tiles browser routes."""

from flask import Blueprint, render_template, current_app, send_file, abort
from pathlib import Path
import gzip

tiles_bp = Blueprint('tiles', __name__)

@tiles_bp.route('/')
def index():
    """Tiles browser main page."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        regions_dir = tiles_dir / 'regions'
        
        regions = []
        
        if regions_dir.exists():
            for region_dir in regions_dir.iterdir():
                if region_dir.is_dir():
                    # Count tiles
                    tile_files = list(region_dir.glob('*.svg.gz'))
                    
                    if tile_files:  # Only show regions with tiles
                        # Calculate size
                        total_size = sum(f.stat().st_size for f in tile_files)
                        
                        # Load metadata if available
                        metadata_file = region_dir / 'metadata.json'
                        metadata = None
                        if metadata_file.exists():
                            import json
                            try:
                                with metadata_file.open('r') as f:
                                    metadata = json.load(f)
                            except:
                                pass
                        
                        regions.append({
                            'name': region_dir.name,
                            'display_name': region_dir.name.replace('-', ' ').title(),
                            'tile_count': len(tile_files),
                            'size_mb': round(total_size / (1024 * 1024), 1),
                            'metadata': metadata
                        })
        
        # Sort by name
        regions.sort(key=lambda x: x['name'])
        
        return render_template('admin/tiles.html', regions=regions)
        
    except Exception as e:
        return render_template('admin/tiles.html', regions=[], error=str(e))

@tiles_bp.route('/regions/<region_name>/')
def region_tiles(region_name):
    """Browse tiles for a specific region."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        region_dir = tiles_dir / 'regions' / region_name
        
        if not region_dir.exists():
            abort(404, f"Region '{region_name}' not found")
        
        # Get all tile files
        tile_files = list(region_dir.glob('*.svg.gz'))
        
        if not tile_files:
            return render_template('admin/region_tiles.html', 
                                 region_name=region_name, 
                                 tiles=[], 
                                 message="No tiles found in this region")
        
        # Process tile information
        tiles = []
        for tile_file in sorted(tile_files):
            # Extract coordinates from filename (e.g., "43.650_-79.380.svg.gz")
            filename = tile_file.stem.replace('.svg', '')  # Remove .svg from .svg.gz
            try:
                lat_str, lng_str = filename.split('_')
                lat = float(lat_str)
                lng = float(lng_str)
                
                # Get file info
                size_kb = round(tile_file.stat().st_size / 1024, 1)
                
                tiles.append({
                    'filename': tile_file.name,
                    'display_name': f"Tile {lat:.3f}, {lng:.3f}",
                    'lat': lat,
                    'lng': lng,
                    'size_kb': size_kb,
                    'url': f"/tiles/regions/{region_name}/{tile_file.name}"
                })
            except (ValueError, IndexError):
                # Skip files that don't match expected pattern
                continue
        
        # Load metadata
        metadata_file = region_dir / 'metadata.json'
        metadata = None
        if metadata_file.exists():
            import json
            try:
                with metadata_file.open('r') as f:
                    metadata = json.load(f)
            except:
                pass
        
        # Calculate total size
        total_size = sum(t['size_kb'] for t in tiles)
        
        region_info = {
            'name': region_name,
            'display_name': region_name.replace('-', ' ').title(),
            'tile_count': len(tiles),
            'total_size_kb': round(total_size, 1),
            'total_size_mb': round(total_size / 1024, 1),
            'metadata': metadata
        }
        
        return render_template('admin/region_tiles.html', 
                             region_name=region_name,
                             region_info=region_info,
                             tiles=tiles)
        
    except Exception as e:
        abort(500, f"Error loading tiles: {str(e)}")

@tiles_bp.route('/regions/<region_name>/<tile_filename>')
def serve_tile(region_name, tile_filename):
    """Serve a specific tile file."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        tile_path = tiles_dir / 'regions' / region_name / tile_filename
        
        if not tile_path.exists():
            abort(404, f"Tile '{tile_filename}' not found in region '{region_name}'")
        
        # Check if it's a compressed file
        if tile_filename.endswith('.svg.gz'):
            # Serve decompressed SVG
            with gzip.open(tile_path, 'rt', encoding='utf-8') as f:
                content = f.read()
            
            from flask import Response
            return Response(content, mimetype='image/svg+xml')
        else:
            # Serve file directly
            return send_file(tile_path)
            
    except Exception as e:
        abort(500, f"Error serving tile: {str(e)}")

@tiles_bp.route('/regions/<region_name>/<tile_filename>/raw')
def serve_tile_raw(region_name, tile_filename):
    """Serve a tile file in its raw compressed format."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        tile_path = tiles_dir / 'regions' / region_name / tile_filename
        
        if not tile_path.exists():
            abort(404, f"Tile '{tile_filename}' not found in region '{region_name}'")
        
        return send_file(tile_path, as_attachment=True)
        
    except Exception as e:
        abort(500, f"Error serving raw tile: {str(e)}")