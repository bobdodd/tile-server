#!/usr/bin/env python3
"""Simple OSM file test."""

import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def simple_osm_test():
    """Basic OSM file validation test."""
    print("=== Simple OSM Test ===")
    
    try:
        import osmium
        print("✓ osmium imported successfully")
        
        # Test with minimal handler
        class SimpleHandler(osmium.SimpleHandler):
            def __init__(self):
                super().__init__()
                self.count = 0
                
            def node(self, n):
                self.count += 1
                if self.count >= 100:  # Stop after first 100 nodes
                    raise osmium.StopIteration()
        
        handler = SimpleHandler()
        osm_file = "/home/bob/Documents/map/tile-server/data/osm_cache/ontario-latest.osm.pbf"
        
        print(f"Testing OSM file: {osm_file}")
        print("Reading first 100 nodes...")
        
        try:
            handler.apply_file(osm_file)
        except osmium.StopIteration:
            pass  # Expected when we hit our limit
        
        print(f"✓ Successfully read {handler.count} nodes")
        print("OSM file appears to be valid")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_osm_test()