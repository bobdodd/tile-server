"""API endpoints for missing tile reporting."""

from flask import Blueprint, request, jsonify
from datetime import datetime

missing_api_bp = Blueprint('missing_api', __name__)

@missing_api_bp.route('/missing-tile', methods=['POST'])
def report_missing_tile():
    """Report a missing tile from the main app."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        lat = data.get('lat')
        lng = data.get('lng')
        
        if lat is None or lng is None:
            return jsonify({'error': 'lat and lng are required'}), 400
        
        # Round to tile boundaries
        tile_lat = round(float(lat), 2)
        tile_lng = round(float(lng), 2)
        
        # Store missing tile request
        missing_tile_data = {
            'lat': tile_lat,
            'lng': tile_lng,
            'requested_at': datetime.now().isoformat(),
            'context': data.get('context', {}),
            'user_location': data.get('user_location'),
            'timestamp': data.get('timestamp')
        }
        
        # TODO: Store in database for batch processing
        store_missing_tile_request(missing_tile_data)
        
        return jsonify({
            'status': 'recorded',
            'message': 'Missing tile request recorded',
            'tile_coordinates': {'lat': tile_lat, 'lng': tile_lng}
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def store_missing_tile_request(tile_data):
    """Store missing tile request for later processing."""
    # For now, just log it
    print(f"Missing tile request: {tile_data['lat']}, {tile_data['lng']} at {tile_data['requested_at']}")
    
    # TODO: Implement database storage
    # - Check if already in queue
    # - Increment request count if exists
    # - Add to generation queue if high priority
    pass