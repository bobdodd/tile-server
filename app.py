"""Main Flask application for the tile generation server."""

from flask import Flask, send_from_directory, jsonify, render_template
from pathlib import Path
import os
import json

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Ensure required directories exist
    Path(app.config['TILES_DIR']).mkdir(exist_ok=True)
    Path(app.config['DATA_DIR']).mkdir(exist_ok=True)
    
    # Register blueprints
    register_blueprints(app)
    
    # Main routes
    @app.route('/')
    def index():
        """Main landing page."""
        return render_template('index.html')
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'server': 'tile-generation-server',
            'version': '1.0.0'
        })
    
    return app

def register_blueprints(app):
    """Register all blueprints."""
    
    # Admin interface
    from admin.routes.dashboard import dashboard_bp
    from admin.routes.regions import regions_bp
    from admin.routes.tiles import tiles_bp
    from admin.routes.generation import generation_bp
    
    app.register_blueprint(dashboard_bp, url_prefix='/admin')
    app.register_blueprint(regions_bp, url_prefix='/admin/regions')
    app.register_blueprint(tiles_bp, url_prefix='/admin/tiles')
    app.register_blueprint(generation_bp, url_prefix='/admin/generation')
    
    # API endpoints
    from api.tiles import tiles_api_bp
    from api.missing import missing_api_bp
    
    app.register_blueprint(tiles_api_bp, url_prefix='/api')
    app.register_blueprint(missing_api_bp, url_prefix='/api')
    
    # Direct tile serving (high performance)
    @app.route('/tiles/<path:filepath>')
    def serve_tile(filepath):
        """Serve tile files directly."""
        tiles_dir = Path(app.config['TILES_DIR'])
        return send_from_directory(tiles_dir, filepath)

if __name__ == '__main__':
    # Development server
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)