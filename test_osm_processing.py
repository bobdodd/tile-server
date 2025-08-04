#!/usr/bin/env python3
"""Test OSM processing in isolation."""

import sys
import os
import time
import signal
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def timeout_handler(signum, frame):
    print("\n⏰ Timeout reached - OSM processing is hanging!")
    sys.exit(1)

def test_osm_processing():
    """Test OSM processing with timeout."""
    print("=== OSM Processing Test ===")
    
    try:
        import osmium
        from tile_generation.osm_processor import OSMHandler
        print("✓ Imported osmium and OSMHandler")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Small test bounds
    bounds = {
        'north': 43.641,
        'south': 43.640,
        'east': -79.379,
        'west': -79.380
    }
    
    osm_file = Path("/home/bob/Documents/map/tile-server/data/osm_cache/ontario-latest.osm.pbf")
    
    if not osm_file.exists():
        print(f"❌ OSM file not found: {osm_file}")
        return
    
    print(f"Testing with OSM file: {osm_file}")
    print(f"File size: {osm_file.stat().st_size / (1024*1024):.1f} MB")
    print(f"Bounds: {bounds}")
    
    # Set timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout
    
    try:
        print("Creating OSMHandler...")
        handler = OSMHandler(bounds)
        print("✓ OSMHandler created")
        
        print("Starting OSM file processing...")
        print("This will timeout after 30 seconds if it hangs...")
        
        start_time = time.time()
        handler.apply_file(str(osm_file), locations=True)
        elapsed = time.time() - start_time
        
        signal.alarm(0)  # Cancel timeout
        print(f"✓ OSM processing completed in {elapsed:.1f} seconds")
        
        # Show what was found
        total_features = sum(len(features) for features in handler.features.values())
        print(f"Total features found: {total_features}")
        
        for feature_type, features in handler.features.items():
            if features:
                print(f"  {feature_type}: {len(features)}")
        
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        print(f"❌ Error during OSM processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_osm_processing()