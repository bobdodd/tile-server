"""API endpoints for tile serving."""

from flask import Blueprint, jsonify, send_file, request, current_app
from pathlib import Path
import json

tiles_api_bp = Blueprint('tiles_api', __name__)

@tiles_api_bp.route('/tile/<region>/<tile_name>')
def serve_tile(region, tile_name):
    """Serve a specific tile file."""
    tile_path = Path(current_app.config['TILES_DIR']) / 'regions' / region / tile_name
    
    if tile_path.exists():
        return send_file(tile_path, mimetype='image/svg+xml')
    else:
        # Report missing tile
        lat_lng = tile_name.replace('.svg.gz', '').split('_')
        if len(lat_lng) == 2:
            try:
                lat, lng = float(lat_lng[0]), float(lat_lng[1])
                report_missing_tile(lat, lng, region)
            except ValueError:
                pass
        
        return jsonify({'error': 'Tile not found'}), 404

@tiles_api_bp.route('/regions')
def list_available_regions():
    """List all available regions and their coverage."""
    regions = []
    regions_dir = Path(current_app.config['TILES_DIR']) / 'regions'
    
    if regions_dir.exists():
        for region_dir in regions_dir.iterdir():
            if region_dir.is_dir():
                metadata_file = region_dir / 'metadata.json'
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                        
                        # Add tile count
                        tile_files = list(region_dir.glob('*.svg.gz'))
                        metadata['available_tiles'] = len(tile_files)
                        regions.append(metadata)
                        
                    except Exception as e:
                        print(f"Error reading metadata for {region_dir}: {e}")
    
    return jsonify({'regions': regions})

@tiles_api_bp.route('/region/<region_name>/tiles')
def list_region_tiles(region_name):
    """List all tiles in a specific region."""
    region_dir = Path(current_app.config['TILES_DIR']) / 'regions' / region_name
    
    if not region_dir.exists():
        return jsonify({'error': 'Region not found'}), 404
    
    tiles = []
    for tile_file in region_dir.glob('*.svg.gz'):
        # Parse coordinates from filename
        name_parts = tile_file.stem.split('_')
        if len(name_parts) == 2:
            try:
                lat, lng = float(name_parts[0]), float(name_parts[1])
                tiles.append({
                    'filename': tile_file.name,
                    'lat': lat,
                    'lng': lng,
                    'size_bytes': tile_file.stat().st_size,
                    'url': f'/api/tile/{region_name}/{tile_file.name}'
                })
            except ValueError:
                continue
    
    return jsonify({
        'region': region_name,
        'tiles': tiles,
        'total_tiles': len(tiles)
    })

def report_missing_tile(lat, lng, region):
    """Report a missing tile request."""
    # This would store the missing tile request in database
    # For now, just log it
    print(f"Missing tile requested: {lat}, {lng} in region {region}")
    
    # TODO: Store in database for batch processing
    pass