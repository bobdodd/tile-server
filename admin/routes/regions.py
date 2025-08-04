"""Regions management routes."""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, jsonify
from pathlib import Path
from tile_generation.builder import TileBuilder
import json

regions_bp = Blueprint('regions', __name__)

@regions_bp.route('/')
def index():
    """Regions management page."""
    try:
        builder = TileBuilder()
        regions = builder.get_available_regions()
        
        # Get detailed stats for each region
        for region in regions:
            region_name = region.get('name')
            if region_name:
                # Count tiles
                tiles_dir = Path(current_app.config['TILES_DIR'])
                region_dir = tiles_dir / 'regions' / region_name
                if region_dir.exists():
                    tile_files = list(region_dir.glob('*.svg.gz'))
                    region['actual_tile_count'] = len(tile_files)
                    # Calculate size
                    total_size = sum(f.stat().st_size for f in tile_files)
                    region['size_mb'] = round(total_size / (1024 * 1024), 1)
                else:
                    region['actual_tile_count'] = 0
                    region['size_mb'] = 0
        
        return render_template('admin/regions.html', regions=regions)
    except Exception as e:
        flash(f'Error loading regions: {str(e)}', 'error')
        return render_template('admin/regions.html', regions=[])

@regions_bp.route('/create')
def create():
    """Create new region form."""
    return render_template('admin/create_region.html')

@regions_bp.route('/create', methods=['POST'])
def create_region():
    """Create a new region."""
    try:
        name = request.form.get('name', '').strip()
        display_name = request.form.get('display_name', '').strip()
        
        # Bounds
        north = float(request.form.get('north', 0))
        south = float(request.form.get('south', 0))
        east = float(request.form.get('east', 0))
        west = float(request.form.get('west', 0))
        
        if not name or not display_name:
            flash('Name and display name are required', 'error')
            return redirect(url_for('regions.create'))
        
        if north <= south or east <= west:
            flash('Invalid bounds: north must be > south, east must be > west', 'error')
            return redirect(url_for('regions.create'))
        
        bounds = {
            'north': north,
            'south': south,
            'east': east,
            'west': west
        }
        
        # Start tile generation for new region
        builder = TileBuilder()
        result = builder.generate_tiles_for_region(name, bounds)
        
        if result.get('status') == 'completed':
            flash(f'Successfully created region "{display_name}" with {result.get("successful_tiles", 0)} tiles', 'success')
        else:
            flash(f'Region creation failed: {result.get("error", "Unknown error")}', 'error')
        
        return redirect(url_for('regions.index'))
        
    except ValueError as e:
        flash('Invalid coordinate values', 'error')
        return redirect(url_for('regions.create'))
    except Exception as e:
        flash(f'Error creating region: {str(e)}', 'error')
        return redirect(url_for('regions.create'))

@regions_bp.route('/<region_name>')
def region_detail(region_name):
    """Show details for a specific region."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        metadata_file = tiles_dir / 'regions' / region_name / 'metadata.json'
        
        if not metadata_file.exists():
            flash(f'Region "{region_name}" not found', 'error')
            return redirect(url_for('regions.index'))
        
        # Load metadata
        with metadata_file.open('r') as f:
            metadata = json.load(f)
        
        # Get tile files
        region_dir = tiles_dir / 'regions' / region_name
        tile_files = list(region_dir.glob('*.svg.gz'))
        
        # Calculate stats
        total_size = sum(f.stat().st_size for f in tile_files)
        
        region_stats = {
            'metadata': metadata,
            'tile_count': len(tile_files),
            'size_mb': round(total_size / (1024 * 1024), 1),
            'tiles': [f.name for f in sorted(tile_files)]
        }
        
        return render_template('admin/region_detail.html', region_name=region_name, stats=region_stats)
        
    except Exception as e:
        flash(f'Error loading region details: {str(e)}', 'error')
        return redirect(url_for('regions.index'))

@regions_bp.route('/<region_name>/delete', methods=['POST'])
def delete_region(region_name):
    """Delete a region and all its tiles."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        region_dir = tiles_dir / 'regions' / region_name
        
        if not region_dir.exists():
            flash(f'Region "{region_name}" not found', 'error')
            return redirect(url_for('regions.index'))
        
        # Count tiles before deletion
        tile_files = list(region_dir.glob('*.svg.gz'))
        tile_count = len(tile_files)
        
        # Delete the entire region directory
        import shutil
        shutil.rmtree(region_dir)
        
        flash(f'Successfully deleted region "{region_name}" and {tile_count} tiles', 'success')
        return redirect(url_for('regions.index'))
        
    except Exception as e:
        flash(f'Error deleting region: {str(e)}', 'error')
        return redirect(url_for('regions.index'))