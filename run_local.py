#!/usr/bin/env python3
"""
Local Mac development server for tile generation and management.
Manages tiles locally and uploads to SiteGround for serving.
"""

import os
import sys
from pathlib import Path
from flask import Flask
from config import DevelopmentConfig

def create_app():
    """Create Flask application for local development."""
    # Set template and static folders explicitly
    app = Flask(__name__, 
                template_folder='admin/templates',
                static_folder='admin/static')
    app.config.from_object(DevelopmentConfig)
    
    # Ensure required directories exist
    for directory in [app.config['DATA_DIR'], app.config['TILES_DIR']]:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Register blueprints
    from admin.routes.dashboard import dashboard_bp
    from admin.routes.regions import regions_bp
    from admin.routes.tiles import tiles_bp
    from admin.routes.generation import generation_bp
    from api.tiles import tiles_api_bp
    from api.missing import missing_api_bp
    
    app.register_blueprint(dashboard_bp, url_prefix='/admin')
    app.register_blueprint(regions_bp, url_prefix='/admin/regions')
    app.register_blueprint(tiles_bp, url_prefix='/admin/tiles')
    app.register_blueprint(generation_bp, url_prefix='/admin/generation')
    app.register_blueprint(tiles_api_bp, url_prefix='/api')
    app.register_blueprint(missing_api_bp, url_prefix='/api')
    
    # Main route
    @app.route('/')
    def index():
        return '''
        <h1>Tile Generation Server - Local Mac Development</h1>
        <p>This server generates tiles locally and uploads them to SiteGround for serving.</p>
        <ul>
            <li><a href="/admin/">Admin Interface</a> - Manage tiles and regions</li>
            <li><a href="/api/regions">API</a> - View available regions</li>
            <li><a href="/tiles/">Browse Local Tiles</a> - View generated tile files</li>
        </ul>
        <h2>SiteGround Configuration</h2>
        <p>Set these environment variables or create a .env file:</p>
        <pre>
SITEGROUND_HOST=your-domain.com
SITEGROUND_USERNAME=your-ftp-username
SITEGROUND_PASSWORD=your-ftp-password
        </pre>
        '''
    
    # Serve local tiles
    from flask import send_from_directory, abort
    import os
    
    @app.route('/tiles/')
    @app.route('/tiles/<path:filename>')
    def serve_tiles(filename=None):
        tiles_dir = Path('tiles')
        
        if filename is None:
            # List available regions
            regions_dir = tiles_dir / 'regions'
            if not regions_dir.exists():
                return '<h1>No Tiles Found</h1><p>No tile regions have been generated yet.</p>'
            
            regions = []
            for region_dir in regions_dir.iterdir():
                if region_dir.is_dir():
                    tile_count = len(list(region_dir.glob('*.svg.gz')))
                    if tile_count > 0:
                        regions.append((region_dir.name, tile_count))
            
            if not regions:
                return '<h1>No Tiles Found</h1><p>No tile regions have been generated yet.</p>'
            
            html = '<h1>Local Tile Regions</h1><ul>'
            for region_name, tile_count in regions:
                html += f'<li><a href="/tiles/regions/{region_name}/">{region_name.replace("-", " ").title()}</a> - {tile_count} tiles</li>'
            html += '</ul>'
            return html
        
        # Serve specific file
        try:
            return send_from_directory(tiles_dir, filename)
        except FileNotFoundError:
            abort(404)
    
    return app

def main():
    """Run the local development server."""
    # Load environment variables if .env exists
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    
    app = create_app()
    
    print("🍎 Tile Generation Server - Local Mac Development")
    print("=" * 50)
    print(f"Server: http://{app.config['HOST']}:{app.config['PORT']}")
    print(f"Admin:  http://{app.config['HOST']}:{app.config['PORT']}/admin/")
    print(f"API:    http://{app.config['HOST']}:{app.config['PORT']}/api/regions")
    print("=" * 50)
    
    if not (os.getenv('SITEGROUND_HOST') and os.getenv('SITEGROUND_USERNAME')):
        print("⚠️  SiteGround upload not configured")
        print("   Create .env file with SITEGROUND_HOST, SITEGROUND_USERNAME, SITEGROUND_PASSWORD")
    else:
        print("✅ SiteGround upload configured")
    
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == '__main__':
    main()