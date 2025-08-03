"""Admin dashboard routes."""

from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, jsonify
from pathlib import Path
from admin.siteground_upload import SiteGroundUploader
import json

dashboard_bp = Blueprint('dashboard', __name__)

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
        'siteground_configured': _check_siteground_config()
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
    
    return stats

def _check_siteground_config():
    """Check if SiteGround upload is configured."""
    import os
    return bool(os.environ.get('SITEGROUND_HOST') and os.environ.get('SITEGROUND_USERNAME'))