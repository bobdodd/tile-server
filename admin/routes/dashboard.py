"""Admin dashboard routes."""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, jsonify
from pathlib import Path
from admin.siteground_upload import SiteGroundUploader
from tile_generation.builder import TileBuilder
import json
import threading
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# Global progress storage for active operations
active_operations = {}

@dashboard_bp.route('/')
def index():
    """Main admin dashboard."""
    # Get statistics
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', stats=stats)

@dashboard_bp.route('/upload/<region_name>', methods=['POST'])
def upload_region(region_name):
    """Upload a region's tiles to SiteGround."""
    uploader = SiteGroundUploader()
    success, message = uploader.upload_region_tiles(region_name)
    
    if success:
        flash(f'Successfully uploaded {region_name}: {message}', 'success')
    else:
        flash(f'Failed to upload {region_name}: {message}', 'error')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/sync-all', methods=['POST'])
def sync_all():
    """Upload all regions to SiteGround."""
    uploader = SiteGroundUploader()
    success, results = uploader.sync_all_regions()
    
    if success:
        successful = results['successful_regions']
        total = results['total_regions']
        flash(f'Sync complete: {successful}/{total} regions uploaded successfully', 'success')
    else:
        flash(f'Sync failed: {results}', 'error')
    
    return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/test-connection')
def test_connection():
    """Test SiteGround FTP connection."""
    uploader = SiteGroundUploader()
    success, message = uploader.test_connection()
    
    return jsonify({
        'success': success,
        'message': message
    })

@dashboard_bp.route('/update-tiles/<region_name>', methods=['POST'])
def update_tiles(region_name):
    """Update/regenerate existing tiles for a region."""
    try:
        # Get region metadata to find bounds
        region_metadata = get_region_metadata(region_name)
        if not region_metadata:
            flash(f'Region {region_name} not found or has no metadata', 'error')
            return redirect(url_for('dashboard.index'))
        
        bounds = region_metadata.get('bounds')
        if not bounds:
            flash(f'No bounds found for region {region_name}', 'error')
            return redirect(url_for('dashboard.index'))
        
        # Start tile generation in background thread
        builder = TileBuilder()
        thread = threading.Thread(
            target=background_tile_generation,
            args=(builder, region_name, bounds, 'update')
        )
        thread.daemon = True
        thread.start()
        
        flash(f'Started updating tiles for {region_name}. Check back for progress.', 'info')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        flash(f'Error starting tile update: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@dashboard_bp.route('/progress/<region_name>')
def get_progress(region_name):
    """Get tile generation progress for a region."""
    try:
        # Check global progress storage first
        if region_name in active_operations:
            progress = active_operations[region_name]
            
            # Calculate estimated completion time
            if progress.get('status') == 'processing' and progress.get('start_time'):
                start_time = datetime.fromisoformat(progress['start_time'])
                elapsed = (datetime.now() - start_time).total_seconds()
                completed = progress.get('completed_tiles', 0)
                total = progress.get('total_tiles', 1)
                
                if completed > 0:
                    avg_time_per_tile = elapsed / completed
                    remaining_tiles = total - completed
                    eta_seconds = remaining_tiles * avg_time_per_tile
                    
                    if eta_seconds < 60:
                        progress['estimated_completion'] = f"{int(eta_seconds)}s"
                    elif eta_seconds < 3600:
                        progress['estimated_completion'] = f"{int(eta_seconds/60)}m"
                    else:
                        progress['estimated_completion'] = f"{int(eta_seconds/3600)}h {int((eta_seconds%3600)/60)}m"
                else:
                    progress['estimated_completion'] = "Calculating..."
            
            return jsonify(progress)
        
        # Fallback to builder progress for backward compatibility
        builder = TileBuilder()
        progress = builder.get_generation_progress()
        
        if progress and progress.get('region') == region_name:
            return jsonify(progress)
        else:
            return jsonify({'status': 'not_running', 'region': region_name})
            
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})

@dashboard_bp.route('/update-all-regions', methods=['POST'])
def update_all_regions():
    """Update/regenerate tiles for all existing regions."""
    try:
        stats = get_dashboard_stats()
        regions_to_update = []
        
        # Collect all regions that have local tiles
        for region in stats['regions']:
            if region['local_tile_count'] > 0:
                region_metadata = get_region_metadata(region['region_id'])
                if region_metadata and region_metadata.get('bounds'):
                    regions_to_update.append({
                        'name': region['region_id'],
                        'bounds': region_metadata['bounds']
                    })
        
        if not regions_to_update:
            flash('No regions found with existing tiles to update', 'warning')
            return redirect(url_for('dashboard.index'))
        
        # Start background thread to update all regions
        thread = threading.Thread(
            target=background_update_all_regions,
            args=(regions_to_update,)
        )
        thread.daemon = True
        thread.start()
        
        flash(f'Started updating tiles for {len(regions_to_update)} regions. Check back for progress.', 'info')
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        flash(f'Error starting bulk update: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

def get_dashboard_stats():
    """Calculate dashboard statistics including SiteGround server status."""
    tiles_dir = Path(current_app.config['TILES_DIR'])
    regions_dir = tiles_dir / 'regions'
    
    stats = {
        'total_regions': 0,
        'total_tiles': 0,
        'total_size_mb': 0,
        'server_tiles': 0,
        'regions': [],
        'siteground_configured': _check_siteground_config(),
        'osm_cache': {}
    }
    
    # Get SiteGround server regions if configured
    server_regions = {}
    if stats['siteground_configured']:
        try:
            uploader = SiteGroundUploader()
            server_regions = uploader.get_all_server_regions()
            stats['server_tiles'] = sum(region['tile_count'] for region in server_regions.values())
        except Exception as e:
            print(f"Error checking SiteGround server: {e}")
    
    # Check local regions
    if regions_dir.exists():
        for region_dir in regions_dir.iterdir():
            if region_dir.is_dir():
                region_name = region_dir.name
                
                # Count local tiles
                tile_files = list(region_dir.glob('*.svg.gz'))
                local_tile_count = len(tile_files)
                
                if local_tile_count > 0:  # Only show regions with actual tiles
                    # Calculate size
                    total_size = sum(f.stat().st_size for f in tile_files)
                    size_mb = total_size / (1024 * 1024)
                    
                    # Check server status
                    server_tile_count = 0
                    server_status = 'local_only'
                    
                    if region_name in server_regions:
                        server_tile_count = server_regions[region_name]['tile_count']
                        if server_tile_count == local_tile_count:
                            server_status = 'synced'
                        elif server_tile_count > 0:
                            server_status = 'partial'
                        else:
                            server_status = 'local_only'
                    
                    region_stats = {
                        'name': region_name.replace('-', ' ').title(),
                        'region_id': region_name,
                        'local_tile_count': local_tile_count,
                        'server_tile_count': server_tile_count,
                        'size_mb': size_mb,
                        'status': server_status
                    }
                    
                    stats['regions'].append(region_stats)
                    stats['total_tiles'] += local_tile_count
                    stats['total_size_mb'] += size_mb
                    stats['total_regions'] += 1
    
    # Add server-only regions (regions that exist on server but not locally)
    for server_region_name, server_data in server_regions.items():
        if not any(r['region_id'] == server_region_name for r in stats['regions']):
            region_stats = {
                'name': server_region_name.replace('-', ' ').title(),
                'region_id': server_region_name,
                'local_tile_count': 0,
                'server_tile_count': server_data['tile_count'],
                'size_mb': 0,  # Can't calculate without downloading
                'status': 'server_only'
            }
            stats['regions'].append(region_stats)
            stats['total_regions'] += 1
    
    # Get OSM cache status
    try:
        builder = TileBuilder()
        stats['osm_cache'] = builder.get_osm_cache_status()
    except Exception as e:
        print(f"Error getting OSM cache status: {e}")
        stats['osm_cache'] = {}
    
    return stats

def get_region_metadata(region_name):
    """Get metadata for a specific region."""
    try:
        tiles_dir = Path(current_app.config['TILES_DIR'])
        metadata_file = tiles_dir / 'regions' / region_name / 'metadata.json'
        
        if metadata_file.exists():
            with metadata_file.open('r') as f:
                return json.load(f)
        return None
    except Exception:
        return None

def background_tile_generation(builder, region_name, bounds, operation_type):
    """Background thread function for tile generation."""
    try:
        # Initialize progress tracking
        active_operations[region_name] = {
            'status': 'initializing',
            'region': region_name,
            'total_tiles': 0,
            'completed_tiles': 0,
            'current_tile': None,
            'start_time': datetime.now().isoformat(),
            'operation_type': operation_type
        }
        
        print(f"Starting {operation_type} for region {region_name}")
        
        # Custom progress callback to update global storage
        def progress_callback(current_progress):
            if region_name in active_operations:
                active_operations[region_name].update(current_progress)
        
        # Run tile generation and monitor progress
        result = builder.generate_tiles_for_region(region_name, bounds)
        
        # Monitor the builder's internal progress and update our global progress
        def monitor_progress():
            import time
            while region_name in active_operations and active_operations[region_name]['status'] not in ['completed', 'error']:
                builder_progress = builder.get_generation_progress()
                if builder_progress and builder_progress.get('region') == region_name:
                    active_operations[region_name].update(builder_progress)
                time.sleep(1)  # Check every second
        
        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()
        
        # Update final status
        if region_name in active_operations:
            active_operations[region_name]['status'] = result.get('status', 'completed')
            active_operations[region_name]['completed_tiles'] = result.get('successful_tiles', 0)
            if result.get('status') == 'error':
                active_operations[region_name]['error'] = result.get('error', 'Unknown error')
        
        print(f"Completed {operation_type} for region {region_name}: {result}")
        
        # Clean up after 5 minutes
        def cleanup():
            import time
            time.sleep(300)  # 5 minutes
            if region_name in active_operations:
                del active_operations[region_name]
        
        threading.Thread(target=cleanup, daemon=True).start()
        
    except Exception as e:
        print(f"Error in background tile generation: {e}")
        if region_name in active_operations:
            active_operations[region_name]['status'] = 'error'
            active_operations[region_name]['error'] = str(e)

def background_update_all_regions(regions_to_update):
    """Background thread function for updating all regions."""
    try:
        # Initialize progress for bulk operation
        active_operations['all'] = {
            'status': 'initializing',
            'region': 'all',
            'total_regions': len(regions_to_update),
            'completed_regions': 0,
            'current_region': None,
            'start_time': datetime.now().isoformat(),
            'operation_type': 'bulk_update'
        }
        
        builder = TileBuilder()
        print(f"Starting bulk update for {len(regions_to_update)} regions")
        
        for i, region_info in enumerate(regions_to_update):
            region_name = region_info['name']
            bounds = region_info['bounds']
            
            try:
                # Update progress
                active_operations['all'].update({
                    'status': 'processing',
                    'current_region': region_name,
                    'completed_regions': i
                })
                
                print(f"Updating region {i+1}/{len(regions_to_update)}: {region_name}")
                result = builder.generate_tiles_for_region(region_name, bounds)
                print(f"Completed {region_name}: {result}")
            except Exception as e:
                print(f"Error updating region {region_name}: {e}")
                continue
        
        # Mark as completed
        active_operations['all'].update({
            'status': 'completed',
            'completed_regions': len(regions_to_update),
            'current_region': None
        })
        
        print("Bulk region update completed")
        
        # Clean up after 5 minutes
        def cleanup():
            import time
            time.sleep(300)  # 5 minutes
            if 'all' in active_operations:
                del active_operations['all']
        
        threading.Thread(target=cleanup, daemon=True).start()
        
    except Exception as e:
        print(f"Error in bulk region update: {e}")
        if 'all' in active_operations:
            active_operations['all']['status'] = 'error'
            active_operations['all']['error'] = str(e)

@dashboard_bp.route('/osm-cache-status')
def osm_cache_status():
    """Get OSM cache status for display."""
    try:
        builder = TileBuilder()
        cache_status = builder.get_osm_cache_status()
        return jsonify(cache_status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/update-osm-data', methods=['POST'])
def update_osm_data():
    """Update OSM data cache."""
    province = request.form.get('province')  # Optional, update specific province
    force = request.form.get('force', 'true').lower() == 'true'
    
    try:
        builder = TileBuilder()
        results = builder.update_osm_data(province=province, force=force)
        
        # Count successes and failures
        successful = sum(1 for r in results.values() if r['success'])
        total = len(results)
        
        if successful == total:
            if province:
                flash(f'Successfully updated OSM data for {province}', 'success')
            else:
                flash(f'Successfully updated OSM data for {successful} provinces', 'success')
        else:
            failed = total - successful
            flash(f'Updated {successful}/{total} provinces. {failed} failed.', 'warning')
            
        return redirect(url_for('dashboard.index'))
        
    except Exception as e:
        flash(f'Error updating OSM data: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

def _check_siteground_config():
    """Check if SiteGround upload is configured."""
    import os
    return bool(os.environ.get('SITEGROUND_HOST') and os.environ.get('SITEGROUND_USERNAME'))