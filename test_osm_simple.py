#!/usr/bin/env python3
"""Simplest possible OSM file test."""

import sys
from pathlib import Path
import signal

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def timeout_handler(signum, frame):
    print("\n⏰ Test timed out - this suggests the OSM processing is hanging")
    sys.exit(1)

def test_osm_simple():
    """Test OSM file reading with minimal processing."""
    print("=== Simple OSM File Test ===")
    
    try:
        import osmium
        print("✓ osmium imported successfully")
        
        class CountHandler(osmium.SimpleHandler):
            def __init__(self):
                super().__init__()
                self.node_count = 0
                self.way_count = 0
                self.relation_count = 0
                
            def node(self, n):
                self.node_count += 1
                if self.node_count % 100000 == 0:
                    print(f"  Processed {self.node_count} nodes...")
                
            def way(self, w):
                self.way_count += 1
                if self.way_count % 10000 == 0:
                    print(f"  Processed {self.way_count} ways...")
                    
            def relation(self, r):
                self.relation_count += 1
        
        handler = CountHandler()
        osm_file = "/home/bob/Documents/map/tile-server/data/osm_cache/ontario-latest.osm.pbf"
        
        print(f"Testing OSM file: {osm_file}")
        print("Starting to process file... (will timeout after 60s if hanging)")
        
        # Set 60 second timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)
        
        try:
            handler.apply_file(osm_file, locations=True)
            signal.alarm(0)  # Cancel timeout
            
            print(f"✓ Successfully processed OSM file!")
            print(f"  Nodes: {handler.node_count}")
            print(f"  Ways: {handler.way_count}")
            print(f"  Relations: {handler.relation_count}")
            
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            print(f"❌ Error during processing: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_osm_simple()