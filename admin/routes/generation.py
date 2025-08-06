"""Tile generation management routes."""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, jsonify
from pathlib import Path
from tile_generation.builder import TileBuilder
import json
import threading
from datetime import datetime

generation_bp = Blueprint('generation', __name__)

@generation_bp.route('/')
def index():
    """Generation management main page."""
    try:
        builder = TileBuilder()
        
        # Get OSM cache status
        osm_cache = builder.get_osm_cache_status()
        
        # Get available regions
        regions = builder.get_available_regions()
        
        # Calculate generation statistics
        total_tiles = sum(r.get('tile_count', 0) for r in regions)
        total_regions = len(regions)
        
        # Check for active operations
        from admin.shared_state import active_operations
        active_ops = dict(active_operations)  # Copy to avoid race conditions
        
        stats = {
            'total_regions': total_regions,
            'total_tiles': total_tiles,
            'osm_provinces': len([p for p in osm_cache.values() if p['exists']]),
            'osm_size_gb': round(sum(p['size_mb'] for p in osm_cache.values() if p['exists']) / 1024, 1),
            'active_operations': len(active_ops),
            'osm_cache': osm_cache,
            'regions': regions,
            'active_ops': active_ops
        }
        
        return render_template('admin/generation.html', stats=stats)
        
    except Exception as e:
        flash(f'Error loading generation status: {str(e)}', 'error')
        return render_template('admin/generation.html', stats={})

@generation_bp.route('/queue', endpoint='queue')
def queue_status():
    """Show current generation queue and active operations."""
    try:
        from admin.shared_state import active_operations
        
        # Get active operations
        active_ops = []
        for region_id, operation in active_operations.items():
            active_ops.append({
                'region_id': region_id,
                'region_name': region_id.replace('-', ' ').title() if region_id != 'all' else 'All Regions',
                'status': operation.get('status', 'unknown'),
                'operation_type': operation.get('operation_type', 'unknown'),
                'progress': {
                    'completed': operation.get('completed_tiles', operation.get('completed_regions', 0)),
                    'total': operation.get('total_tiles', operation.get('total_regions', 1)),
                    'percentage': 0
                },
                'start_time': operation.get('start_time'),
                'current_item': operation.get('current_tile', operation.get('current_region')),
                'estimated_completion': operation.get('estimated_completion')
            })
            
            # Calculate percentage
            if active_ops[-1]['progress']['total'] > 0:
                active_ops[-1]['progress']['percentage'] = round(
                    (active_ops[-1]['progress']['completed'] / active_ops[-1]['progress']['total']) * 100
                )
        
        return render_template('admin/generation_queue.html', operations=active_ops)
        
    except Exception as e:
        flash(f'Error loading queue status: {str(e)}', 'error')
        return render_template('admin/generation_queue.html', operations=[])

@generation_bp.route('/tools')
def tools():
    """Generation tools and utilities."""
    try:
        builder = TileBuilder()
        
        # Get system info
        import shutil, subprocess, sys
        
        tools_status = {
            'python_version': sys.version,
            'osmium_available': shutil.which('osmium') is not None,
            'osmium_version': None
        }
        
        # Try to get osmium version
        if tools_status['osmium_available']:
            try:
                result = subprocess.run(['osmium', '--version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    tools_status['osmium_version'] = result.stdout.strip()
            except:
                pass
        
        # Get cache directory info
        cache_dir = builder.data_dir / 'osm_cache'
        cache_info = {
            'path': str(cache_dir),
            'exists': cache_dir.exists(),
            'total_files': 0,
            'total_size_gb': 0
        }
        
        if cache_dir.exists():
            cache_files = list(cache_dir.glob('*.osm.pbf'))
            cache_info['total_files'] = len(cache_files)
            total_size = sum(f.stat().st_size for f in cache_files)
            cache_info['total_size_gb'] = round(total_size / (1024**3), 2)
        
        return render_template('admin/generation_tools.html', 
                             tools_status=tools_status, 
                             cache_info=cache_info)
        
    except Exception as e:
        flash(f'Error loading tools info: {str(e)}', 'error')
        return render_template('admin/generation_tools.html', 
                             tools_status={}, cache_info={})

@generation_bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear OSM data cache."""
    try:
        builder = TileBuilder()
        cache_dir = builder.data_dir / 'osm_cache'
        
        if not cache_dir.exists():
            flash('Cache directory does not exist', 'warning')
            return redirect(url_for('generation.tools'))
        
        # Count files before deletion
        cache_files = list(cache_dir.glob('*.osm.pbf'))
        filtered_files = list(cache_dir.glob('*-filtered.osm.pbf'))
        
        total_files = len(cache_files) + len(filtered_files)
        total_size = sum(f.stat().st_size for f in cache_files + filtered_files)
        
        # Delete files
        for file in cache_files + filtered_files:
            file.unlink()
        
        flash(f'Cleared cache: {total_files} files, {total_size / (1024**2):.1f}MB freed', 'success')
        return redirect(url_for('generation.tools'))
        
    except Exception as e:
        flash(f'Error clearing cache: {str(e)}', 'error')
        return redirect(url_for('generation.tools'))

@generation_bp.route('/cancel/<operation_id>', methods=['POST'])
def cancel_operation(operation_id):
    """Cancel an active generation operation."""
    try:
        from admin.shared_state import active_operations
        
        if operation_id in active_operations:
            # Mark as cancelled (the background thread should check this)
            active_operations[operation_id]['status'] = 'cancelled'
            active_operations[operation_id]['cancelled_at'] = datetime.now().isoformat()
            
            flash(f'Cancelled operation for {operation_id}', 'success')
        else:
            flash(f'Operation {operation_id} not found or already completed', 'warning')
        
        return redirect(url_for('generation.queue'))
        
    except Exception as e:
        flash(f'Error cancelling operation: {str(e)}', 'error')
        return redirect(url_for('generation.queue'))