"""SiteGround file upload utilities."""
import ftplib
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SiteGroundUploader:
    """Handle uploading tiles to SiteGround via FTP/SFTP."""
    
    def __init__(self):
        # Get configuration from environment variables directly
        self.host = os.environ.get('SITEGROUND_HOST', '')
        self.username = os.environ.get('SITEGROUND_USERNAME', '')
        self.password = os.environ.get('SITEGROUND_PASSWORD', '')
        self.remote_tiles_path = 'bobd77.sg-host.com/public_html/tiles/'
        
    def upload_htaccess(self):
        """Upload .htaccess file to fix Content-Encoding headers."""
        if not self._check_credentials():
            return False, "SiteGround credentials not configured"
            
        htaccess_file = Path.cwd() / '.htaccess-tiles'
        if not htaccess_file.exists():
            return False, ".htaccess-tiles file not found"
            
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                
                # Upload .htaccess to tiles directory
                remote_path = f"{self.remote_tiles_path.rstrip('/')}/.htaccess"
                
                with open(htaccess_file, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)
                
                return True, ".htaccess uploaded successfully"
                
        except Exception as e:
            return False, f"Failed to upload .htaccess: {str(e)}"

    def upload_region_tiles(self, region_name):
        """Upload all tiles for a specific region to SiteGround."""
        if not self._check_credentials():
            return False, "SiteGround credentials not configured"
            
        # Get tiles directory from current working directory
        tiles_dir = Path.cwd() / 'tiles'
        local_region_path = tiles_dir / 'regions' / region_name
        
        if not local_region_path.exists():
            return False, f"Region {region_name} not found locally"
            
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                
                # Create flat tiles directory (no region subdirectories)
                remote_tiles_dir = f"{self.remote_tiles_path.rstrip('/')}"
                self._create_remote_directory(ftp, remote_tiles_dir)
                
                # Upload all tiles to flat structure
                uploaded_count = 0
                tile_files = list(local_region_path.glob('*.svg.gz'))
                
                for tile_file in tile_files:
                    # Upload directly to /tiles/ directory (flat structure)
                    remote_file_path = f"{remote_tiles_dir}/{tile_file.name}"
                    
                    with open(tile_file, 'rb') as f:
                        ftp.storbinary(f'STOR {remote_file_path}', f)
                    
                    uploaded_count += 1
                
                # Upload region metadata to a separate metadata directory for management
                metadata_dir = f"{self.remote_tiles_path.rstrip('/')}_metadata"
                self._create_remote_directory(ftp, metadata_dir)
                
                index_file = local_region_path / 'index.json'
                if index_file.exists():
                    remote_index_path = f"{metadata_dir}/{region_name}_index.json"
                    with open(index_file, 'rb') as f:
                        ftp.storbinary(f'STOR {remote_index_path}', f)
                
                # Validate upload by checking for uploaded tiles in flat directory
                try:
                    ftp.cwd(remote_tiles_dir)
                    server_files = []
                    ftp.retrlines('NLST', server_files.append)
                    
                    # Count only the tiles we just uploaded
                    uploaded_tile_names = [f.name for f in tile_files]
                    server_uploaded_count = len([f for f in server_files if f in uploaded_tile_names])
                    
                    if server_uploaded_count == uploaded_count:
                        return True, f"Successfully uploaded and verified {uploaded_count} tiles for {region_name} to flat structure"
                    else:
                        return False, f"Upload incomplete: uploaded {uploaded_count} but found {server_uploaded_count} on server"
                        
                except ftplib.error_perm as e:
                    return False, f"Upload validation failed: cannot access tiles directory - {e}"
                
        except ftplib.all_errors as e:
            error_msg = f"FTP error uploading {region_name}: {e}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error uploading {region_name}: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def upload_single_tile(self, region_name, tile_filename):
        """Upload a single tile file to SiteGround."""
        if not self._check_credentials():
            return False, "SiteGround credentials not configured"
            
        # Get tiles directory from current working directory
        tiles_dir = Path.cwd() / 'tiles'
        local_tile_path = tiles_dir / 'regions' / region_name / tile_filename
        if not local_tile_path.exists():
            return False, f"Tile {tile_filename} not found locally"
            
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                
                remote_region_path = f"{self.remote_tiles_path}regions/{region_name}/"
                self._create_remote_directory(ftp, remote_region_path)
                
                remote_file_path = f"{remote_region_path}{tile_filename}"
                with open(local_tile_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_file_path}', f)
                
                logger.info(f"Uploaded {tile_filename} to SiteGround")
                return True, f"Uploaded {tile_filename}"
                
        except ftplib.all_errors as e:
            logger.error(f"FTP error uploading {tile_filename}: {e}")
            return False, f"Upload failed: {e}"
        except Exception as e:
            logger.error(f"Error uploading {tile_filename}: {e}")
            return False, f"Upload failed: {e}"
    
    def sync_all_regions(self):
        """Upload all local regions to SiteGround."""
        if not self._check_credentials():
            return False, "SiteGround credentials not configured"
            
        # Get tiles directory from current working directory
        tiles_dir = Path.cwd() / 'tiles' 
        regions_dir = tiles_dir / 'regions'
        if not regions_dir.exists():
            return False, "No regions found locally"
            
        results = {}
        for region_dir in regions_dir.iterdir():
            if region_dir.is_dir():
                success, message = self.upload_region_tiles(region_dir.name)
                results[region_dir.name] = {'success': success, 'message': message}
        
        total_regions = len(results)
        successful_regions = len([r for r in results.values() if r['success']])
        
        return True, {
            'total_regions': total_regions,
            'successful_regions': successful_regions,
            'results': results
        }
    
    def test_connection(self):
        """Test FTP connection to SiteGround."""
        if not self._check_credentials():
            return False, "Credentials not configured"
            
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                return True, "Connection successful"
        except ftplib.all_errors as e:
            return False, f"Connection failed: {e}"
        except Exception as e:
            return False, f"Error: {e}"
    
    def check_region_on_server(self, region_name):
        """Check if region tiles exist on SiteGround flat structure."""
        if not self._check_credentials():
            return False, 0, "Credentials not configured"
            
        # Get local region tiles to know what to look for on server
        tiles_dir = Path.cwd() / 'tiles'
        local_region_path = tiles_dir / 'regions' / region_name
        
        if not local_region_path.exists():
            return False, 0, f"Local region {region_name} not found"
        
        # Get list of tile filenames that should be on server
        local_tile_files = [f.name for f in local_region_path.glob('*.svg.gz')]
        
        if not local_tile_files:
            return False, 0, f"No tiles found in local region {region_name}"
            
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                
                remote_tiles_dir = f"{self.remote_tiles_path.rstrip('/')}"
                
                try:
                    # Check flat tiles directory
                    ftp.cwd(remote_tiles_dir)
                    
                    # List all files in flat directory
                    server_files = []
                    ftp.retrlines('NLST', server_files.append)
                    
                    # Count how many of our region's tiles are on server
                    found_tiles = [f for f in local_tile_files if f in server_files]
                    tile_count = len(found_tiles)
                    
                    # Go back to root
                    ftp.cwd('/')
                    
                    return True, tile_count, f"Found {tile_count}/{len(local_tile_files)} region tiles on server"
                    
                except ftplib.error_perm as e:
                    return False, 0, f"Cannot access tiles directory: {e}"
                    
        except ftplib.all_errors as e:
            return False, 0, f"FTP error: {e}"
        except Exception as e:
            return False, 0, f"Error: {e}"
    
    def get_all_server_regions(self):
        """Get all regions with tiles on SiteGround server (flat structure)."""
        if not self._check_credentials():
            return {}
            
        # Check local regions to know what to look for
        tiles_dir = Path.cwd() / 'tiles' / 'regions'
        if not tiles_dir.exists():
            return {}
            
        try:
            with ftplib.FTP(self.host) as ftp:
                ftp.login(self.username, self.password)
                
                remote_tiles_dir = f"{self.remote_tiles_path.rstrip('/')}"
                
                try:
                    # Get all files from flat tiles directory
                    ftp.cwd(remote_tiles_dir)
                    server_files = []
                    ftp.retrlines('NLST', server_files.append)
                    server_tile_files = [f for f in server_files if f.endswith('.svg.gz')]
                    
                    # Go back to root
                    ftp.cwd('/')
                    
                    # Check each local region against server files
                    server_regions = {}
                    for region_dir in tiles_dir.iterdir():
                        if region_dir.is_dir():
                            region_name = region_dir.name
                            local_tile_files = [f.name for f in region_dir.glob('*.svg.gz')]
                            
                            if local_tile_files:
                                # Count how many region tiles are on server
                                found_tiles = [f for f in local_tile_files if f in server_tile_files]
                                tile_count = len(found_tiles)
                                
                                if tile_count > 0:
                                    server_regions[region_name] = {
                                        'tile_count': tile_count,
                                        'status': 'on_server'
                                    }
                    
                    return server_regions
                    
                except ftplib.error_perm as e:
                    # Tiles directory doesn't exist
                    return {}
                    
        except ftplib.all_errors as e:
            return {}
        except Exception as e:
            return {}
    
    def _check_credentials(self):
        """Check if SiteGround credentials are configured."""
        return all([self.host, self.username, self.password])
    
    def _create_remote_directory(self, ftp, path):
        """Create remote directory structure if it doesn't exist."""
        parts = path.strip('/').split('/')
        current_path = ''
        
        for part in parts:
            if part:  # Skip empty parts
                current_path += f'/{part}' if current_path else part
                try:
                    ftp.mkd(current_path)
                except ftplib.error_perm as e:
                    # Try to change to the directory to verify it exists
                    try:
                        ftp.cwd(current_path)
                        ftp.cwd('/')  # Go back to root
                    except ftplib.error_perm:
                        raise Exception(f"Cannot create or access directory: {current_path}")