#!/usr/bin/env python3
"""Debug script to identify where tile generation hangs."""

import sys
import os
import time
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from tile_generation.builder import TileBuilder
from tile_generation.osm_processor import OSMHandler

def debug_tile_generation():
    """Debug tile generation step by step."""
    print("=== Tile Generation Debug ===")
    
    # Initialize builder
    print("1. Initializing TileBuilder...")
    builder = TileBuilder()
    print("   ✓ TileBuilder initialized")
    
    # Test region and bounds (small area for testing)
    region_name = "toronto-downtown"
    bounds = {
        'north': 43.641,
        'south': 43.640,
        'east': -79.379,
        'west': -79.380
    }
    
    print(f"2. Testing with region: {region_name}")
    print(f"   Bounds: {bounds}")
    
    # Get OSM file
    print("3. Getting OSM file...")
    try:
        osm_file = builder.get_region_osm_file(region_name)
        print(f"   ✓ OSM file found: {osm_file}")
        print(f"   File size: {osm_file.stat().st_size / (1024*1024):.1f} MB")
    except Exception as e:
        print(f"   ❌ Error getting OSM file: {e}")
        return
    
    # Calculate tiles to generate
    print("4. Calculating tile grid...")
    try:
        tiles = builder.calculate_tile_grid(bounds)
        print(f"   ✓ Will generate {len(tiles)} tiles")
        print(f"   First tile: {tiles[0] if tiles else 'None'}")
    except Exception as e:
        print(f"   ❌ Error calculating tiles: {e}")
        return
    
    if not tiles:
        print("   No tiles to generate!")
        return
    
    # Test OSM handler initialization
    print("5. Testing OSM handler initialization...")
    try:
        tile_lat, tile_lng = tiles[0]
        tile_bounds = builder.get_tile_bounds(tile_lat, tile_lng)
        print(f"   Testing tile bounds: {tile_bounds}")
        
        handler = OSMHandler(tile_bounds)
        print("   ✓ OSMHandler initialized")
    except Exception as e:
        print(f"   ❌ Error initializing OSM handler: {e}")
        return
    
    # Test OSM file processing (this is likely where it hangs)
    print("6. Testing OSM file processing...")
    print("   This may take a while for large OSM files...")
    
    start_time = time.time()
    try:
        print("   Starting handler.apply_file()...")
        handler.apply_file(str(osm_file), locations=True)
        elapsed = time.time() - start_time
        print(f"   ✓ OSM processing completed in {elapsed:.1f} seconds")
        
        # Show feature counts
        feature_counts = {k: len(v) for k, v in handler.features.items() if v}
        print(f"   Features found: {feature_counts}")
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"   ❌ Error processing OSM file after {elapsed:.1f}s: {e}")
        return
    
    # Test SVG generation
    print("7. Testing SVG generation...")
    try:
        svg_content = builder.create_tile_svg(tile_lat, tile_lng, handler.features, tile_bounds)
        print(f"   ✓ SVG generated, length: {len(svg_content)} characters")
    except Exception as e:
        print(f"   ❌ Error generating SVG: {e}")
        return
    
    print("=== Debug Complete ===")

if __name__ == "__main__":
    debug_tile_generation()