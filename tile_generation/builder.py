"""Main tile builder - ported and enhanced from build-toronto-tiles.py"""

import os
import sys
import json
import gzip
import math
import requests
import sqlite3
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from datetime import datetime
import tempfile

try:
    import osmium
    from shapely.geometry import Point, LineString, Polygon
    from shapely.ops import transform
    import pyproj
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

from .osm_processor import OSMHandler
from .feature_styles import FEATURE_STYLES

class TileBuilder:
    """Main tile generation class - Flask compatible version."""
    
    def __init__(self, config=None):
        """Initialize tile builder with configuration."""
        self.config = config or {}
        
        # Directory setup
        self.base_dir = Path(__file__).parent.parent
        self.tiles_dir = self.base_dir / 'tiles'
        self.data_dir = self.base_dir / 'data'
        
        # Create directories
        self.tiles_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / 'osm_cache').mkdir(exist_ok=True)
        (self.data_dir / 'logs').mkdir(exist_ok=True)
        
        # Tile configuration
        self.tile_size = 0.01  # degrees per tile
        self.svg_size = 1000   # SVG viewport size
        
        # Feature styles
        self.feature_types = FEATURE_STYLES
        
        # Progress tracking for admin UI
        self.current_progress = {
            'total_tiles': 0,
            'completed_tiles': 0,
            'current_tile': None,
            'status': 'idle',
            'region': None,
            'start_time': None,
            'estimated_completion': None
        }
        
    def generate_tiles_for_region(self, region_name, bounds, options=None):
        """Generate tiles for a specific region - Flask callable."""
        options = options or {}
        
        print(f"Starting tile generation for region: {region_name}")
        
        # Reset progress tracking
        self.current_progress = {
            'total_tiles': 0,
            'completed_tiles': 0,
            'current_tile': None,
            'status': 'initializing',
            'region': region_name,
            'start_time': datetime.now(),
            'estimated_completion': None
        }
        
        try:
            # Create region directory
            region_dir = self.tiles_dir / 'regions' / region_name
            region_dir.mkdir(parents=True, exist_ok=True)
            
            # Calculate tile grid
            tiles_to_generate = self.calculate_tile_grid(bounds)
            self.current_progress['total_tiles'] = len(tiles_to_generate)
            self.current_progress['status'] = 'downloading_data'
            
            print(f"Will generate {len(tiles_to_generate)} tiles")
            
            # Download OSM data for region
            osm_file = self.download_region_data(region_name, bounds)
            
            self.current_progress['status'] = 'processing'
            
            # Generate each tile
            successful_tiles = 0
            failed_tiles = 0
            
            for i, tile_coords in enumerate(tiles_to_generate):
                try:
                    tile_lat, tile_lng = tile_coords
                    
                    # Update progress
                    self.current_progress['current_tile'] = f"{tile_lat:.3f}_{tile_lng:.3f}"
                    self.current_progress['completed_tiles'] = i
                    
                    # Generate the tile
                    tile_file = self.generate_single_tile(tile_lat, tile_lng, region_name, osm_file)
                    
                    if tile_file:
                        successful_tiles += 1
                        # Store tile metadata in database
                        self.store_tile_metadata(tile_lat, tile_lng, region_name, tile_file)
                    else:
                        failed_tiles += 1
                        
                except Exception as e:
                    print(f"Error generating tile {tile_coords}: {e}")
                    failed_tiles += 1
                    continue
            
            # Update region metadata
            self.update_region_metadata(region_name, bounds, successful_tiles)
            
            self.current_progress['status'] = 'completed'
            self.current_progress['completed_tiles'] = successful_tiles
            
            result = {
                'status': 'completed',
                'region': region_name,
                'successful_tiles': successful_tiles,
                'failed_tiles': failed_tiles,
                'total_tiles': len(tiles_to_generate)
            }
            
            print(f"✅ Region generation complete: {successful_tiles} successful, {failed_tiles} failed")
            return result
            
        except Exception as e:
            self.current_progress['status'] = 'error'
            self.current_progress['error'] = str(e)
            print(f"❌ Region generation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'region': region_name
            }
    
    def calculate_tile_grid(self, bounds):
        """Calculate which tiles need to be generated for given bounds."""
        tiles = []
        
        # Calculate tile boundaries
        west_tile = math.floor(bounds['west'] / self.tile_size) * self.tile_size
        east_tile = math.ceil(bounds['east'] / self.tile_size) * self.tile_size
        south_tile = math.floor(bounds['south'] / self.tile_size) * self.tile_size  
        north_tile = math.ceil(bounds['north'] / self.tile_size) * self.tile_size
        
        # Generate tile coordinates
        lat = south_tile
        while lat < north_tile:
            lng = west_tile
            while lng < east_tile:
                tiles.append((round(lat, 3), round(lng, 3)))
                lng += self.tile_size
            lat += self.tile_size
        
        return tiles
    
    def download_region_data(self, region_name, bounds):
        """Download OSM data for the region."""
        # Check cache first
        cache_file = self.data_dir / 'osm_cache' / f"{region_name}.osm.pbf"
        
        if cache_file.exists():
            # Check if cache is recent (within 24 hours)
            cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age < 86400:  # 24 hours
                print(f"Using cached OSM data: {cache_file}")
                return cache_file
        
        print(f"Downloading OSM data for {region_name}...")
        
        # Create Overpass query for the bounds
        overpass_query = f"""
        [out:pbf][timeout:300];
        (
          way["building"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["highway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["waterway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["leisure"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["landuse"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["natural"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["amenity"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["healthcare"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["highway"="bus_stop"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["railway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["public_transport"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["aerialway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          node["aeroway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["railway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["public_transport"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["aerialway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["aeroway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["amenity"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          way["healthcare"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["building"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["leisure"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["landuse"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["amenity"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["healthcare"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["railway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["public_transport"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["aerialway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
          relation["aeroway"]({bounds['south']},{bounds['west']},{bounds['north']},{bounds['east']});
        );
        out body;
        >;
        out skel qt;
        """
        
        # Query Overpass API
        try:
            response = requests.post(
                'https://overpass-api.de/api/interpreter',
                data=overpass_query,
                timeout=300
            )
            response.raise_for_status()
            
            # Save to cache
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded and cached OSM data: {cache_file}")
            return cache_file
            
        except Exception as e:
            print(f"Failed to download OSM data: {e}")
            # Try to use existing cache even if old
            if cache_file.exists():
                print(f"Using old cached data: {cache_file}")
                return cache_file
            raise
    
    def generate_single_tile(self, tile_lat, tile_lng, region_name, osm_file):
        """Generate a single SVG tile."""
        try:
            # Get tile bounds
            bounds = self.get_tile_bounds(tile_lat, tile_lng)
            
            # Process OSM data for this tile
            handler = OSMHandler(bounds)
            handler.apply_file(str(osm_file))
            
            # Create SVG content
            svg_content = self.create_tile_svg(tile_lat, tile_lng, handler.features, bounds)
            
            # Save compressed tile
            tile_filename = f"{tile_lat:.3f}_{tile_lng:.3f}.svg.gz"
            tile_path = self.tiles_dir / 'regions' / region_name / tile_filename
            
            with gzip.open(tile_path, 'wt', encoding='utf-8') as f:
                f.write(svg_content)
            
            return tile_path
            
        except Exception as e:
            print(f"Failed to generate tile {tile_lat}, {tile_lng}: {e}")
            return None
    
    def get_tile_bounds(self, tile_lat, tile_lng):
        """Get bounding box for a tile."""
        return {
            'south': tile_lat,
            'north': tile_lat + self.tile_size,
            'west': tile_lng,
            'east': tile_lng + self.tile_size
        }
    
    def coord_to_svg(self, lat, lng, bounds):
        """Convert lat/lng coordinates to SVG coordinates."""
        # Calculate relative position within tile
        x_ratio = (lng - bounds['west']) / (bounds['east'] - bounds['west'])
        y_ratio = (bounds['north'] - lat) / (bounds['north'] - bounds['south'])  # Flip Y
        
        # Convert to SVG coordinates
        x = x_ratio * self.svg_size
        y = y_ratio * self.svg_size
        
        return x, y
    
    def create_tile_svg(self, tile_lat, tile_lng, features, bounds):
        """Create SVG content for a tile."""
        # Create SVG root element
        svg = Element('svg')
        svg.set('viewBox', f'0 0 {self.svg_size} {self.svg_size}')
        svg.set('xmlns', 'http://www.w3.org/2000/svg')
        svg.set('data-tile-lat', str(tile_lat))
        svg.set('data-tile-lng', str(tile_lng))
        
        # Add style definitions
        style_elem = SubElement(svg, 'style')
        style_elem.text = self.generate_svg_styles()
        
        # Create feature groups
        feature_groups = {}
        for feature_type in features.keys():
            group = SubElement(svg, 'g')
            group.set('id', f'{feature_type}')
            group.set('class', f'feature-group {feature_type}')
            feature_groups[feature_type] = group
        
        # Render features by type
        for feature_type, feature_list in features.items():
            if not feature_list:
                continue
                
            group = feature_groups[feature_type]
            
            for feature in feature_list:
                try:
                    svg_element = self.feature_to_svg(feature_type, feature['geometry'], 
                                                     feature['properties'], bounds)
                    if svg_element is not None:
                        group.append(svg_element)
                except Exception as e:
                    print(f"Error rendering {feature_type} feature: {e}")
                    continue
        
        # Convert to string with pretty formatting
        rough_string = tostring(svg, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def feature_to_svg(self, feature_type, geometry, properties, bounds):
        """Convert a feature geometry to SVG element."""
        if feature_type not in self.feature_types:
            return None
        
        # Determine feature subtype and styling
        feature_subtype = self.determine_feature_subtype(feature_type, properties)
        styles = self.feature_types[feature_type]['styles'].get(feature_subtype, 
                 self.feature_types[feature_type]['styles'].get('default', {}))
        
        # Create SVG element based on geometry type
        if isinstance(geometry, Point):
            return self.create_point_svg(geometry, styles, properties, bounds)
        elif isinstance(geometry, LineString):
            return self.create_line_svg(geometry, styles, properties, bounds, feature_type)
        elif isinstance(geometry, Polygon):
            return self.create_polygon_svg(geometry, styles, properties, bounds)
        
        return None
    
    def create_point_svg(self, geometry, styles, properties, bounds):
        """Create SVG circle element for point geometry."""
        x, y = self.coord_to_svg(geometry.y, geometry.x, bounds)
        
        circle = Element('circle')
        circle.set('cx', str(x))
        circle.set('cy', str(y))
        circle.set('r', str(styles.get('radius', 3)))
        circle.set('fill', styles.get('fill', '#ff0000'))
        circle.set('stroke', styles.get('stroke', '#000000'))
        circle.set('stroke-width', str(styles.get('stroke_width', 1)))
        
        # Add accessibility attributes
        circle.set('role', 'img')
        circle.set('aria-label', self.generate_aria_label(properties))
        
        return circle
    
    def create_line_svg(self, geometry, styles, properties, bounds, feature_type):
        """Create SVG path element for line geometry."""
        if len(geometry.coords) < 2:
            return None
        
        # Convert coordinates to SVG path
        path_data = []
        for i, (lng, lat) in enumerate(geometry.coords):
            x, y = self.coord_to_svg(lat, lng, bounds)
            command = 'M' if i == 0 else 'L'
            path_data.append(f'{command}{x:.1f},{y:.1f}')
        
        # Create path element
        path = Element('path')
        path.set('d', ' '.join(path_data))
        path.set('fill', 'none')
        path.set('stroke', styles.get('color', styles.get('stroke', '#000000')))
        path.set('stroke-width', str(styles.get('width', styles.get('stroke_width', 1))))
        
        if 'dasharray' in styles:
            path.set('stroke-dasharray', styles['dasharray'])
        
        # Add accessibility attributes
        path.set('role', 'img')
        path.set('aria-label', self.generate_aria_label(properties))
        
        # For roads, also create casing if specified
        if feature_type == 'roads' and 'casing' in styles:
            casing = Element('path')
            casing.set('d', ' '.join(path_data))
            casing.set('fill', 'none')
            casing.set('stroke', styles['casing'])
            casing.set('stroke-width', str(styles.get('casing_width', styles.get('width', 1) + 2)))
            
            # Return group with casing and road
            group = Element('g')
            group.append(casing)
            group.append(path)
            return group
        
        return path
    
    def create_polygon_svg(self, geometry, styles, properties, bounds):
        """Create SVG polygon element for polygon geometry."""
        if hasattr(geometry, 'exterior'):
            coords = list(geometry.exterior.coords)
        else:
            coords = list(geometry.coords)
        
        if len(coords) < 3:
            return None
        
        # Convert coordinates to SVG points
        svg_points = []
        for lng, lat in coords:
            x, y = self.coord_to_svg(lat, lng, bounds)
            svg_points.append(f'{x:.1f},{y:.1f}')
        
        polygon = Element('polygon')
        polygon.set('points', ' '.join(svg_points))
        polygon.set('fill', styles.get('fill', '#cccccc'))
        polygon.set('stroke', styles.get('stroke', '#000000'))
        polygon.set('stroke-width', str(styles.get('stroke_width', 1)))
        
        if 'dasharray' in styles:
            polygon.set('stroke-dasharray', styles['dasharray'])
        
        # Add accessibility attributes
        polygon.set('role', 'img') 
        polygon.set('aria-label', self.generate_aria_label(properties))
        
        return polygon
    
    def determine_feature_subtype(self, feature_type, properties):
        """Determine the specific subtype of a feature for styling."""
        if feature_type == 'buildings':
            return properties.get('building', 'yes')
        elif feature_type == 'roads':
            return properties.get('highway', 'road')
        elif feature_type == 'transit':
            # Bus Infrastructure
            if properties.get('highway') == 'bus_stop':
                return 'bus_stop'
            elif properties.get('amenity') == 'bus_station':
                return 'bus_station'
            elif properties.get('highway') == 'bus_guideway':
                return 'bus_guideway'
            
            # Railway Infrastructure
            elif properties.get('railway') in ['station']:
                return 'station'
            elif properties.get('railway') == 'halt':
                return 'halt'
            elif properties.get('railway') == 'subway_entrance':
                return 'subway_entrance'
            elif properties.get('railway') == 'tram_stop':
                return 'tram_stop'
            elif properties.get('railway') == 'rail':
                return 'rail'
            elif properties.get('railway') == 'subway':
                return 'subway'
            elif properties.get('railway') == 'tram':
                return 'tram'
            elif properties.get('railway') == 'light_rail':
                return 'light_rail'
            elif properties.get('railway') == 'narrow_gauge':
                return 'narrow_gauge'
            elif properties.get('railway') == 'funicular':
                return 'funicular'
            elif properties.get('railway') == 'monorail':
                return 'monorail'
            
            # Public Transport
            elif properties.get('public_transport') == 'platform':
                return 'platform'
            elif properties.get('public_transport') == 'stop_position':
                return 'stop_position'
            elif properties.get('public_transport') == 'station':
                return 'station'
            
            # Water Transport
            elif properties.get('amenity') == 'ferry_terminal':
                return 'ferry_terminal'
            
            # Aerial Transport
            elif properties.get('aerialway') == 'cable_car':
                return 'cable_car'
            elif properties.get('aerialway') == 'gondola':
                return 'gondola'
            elif properties.get('aerialway') == 'chair_lift':
                return 'chair_lift'
            elif properties.get('aerialway') == 'drag_lift':
                return 'drag_lift'
            elif properties.get('aerialway') == 'rope_tow':
                return 'rope_tow'
            elif properties.get('aerialway') == 'zip_line':
                return 'zip_line'
            elif properties.get('aerialway') == 'station':
                return 'aerialway_station'
            elif properties.get('aerialway') == 'loading_point':
                return 'loading_point'
            
            # Airport Infrastructure
            elif properties.get('aeroway') == 'terminal':
                return 'terminal'
            elif properties.get('aeroway') == 'gate':
                return 'gate'
            elif properties.get('aeroway') == 'runway':
                return 'runway'
            elif properties.get('aeroway') == 'taxiway':
                return 'taxiway'
            elif properties.get('aeroway') == 'aerodrome':
                return 'aerodrome'
            
            return 'default'
        elif feature_type == 'water':
            if properties.get('waterway'):
                return properties.get('waterway')
            elif properties.get('natural'):
                return properties.get('natural')
            elif properties.get('amenity') == 'fountain':
                return 'fountain'
            return 'water'
        elif feature_type == 'parks':
            return properties.get('leisure', properties.get('landuse', 'park'))
        elif feature_type == 'healthcare':
            # Return the specific healthcare type for styling
            if properties.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary']:
                return properties.get('amenity')
            elif properties.get('healthcare'):
                return properties.get('healthcare')
            return 'default'
        
        return 'default'
    
    def generate_aria_label(self, properties):
        """Generate accessible ARIA label for a feature."""
        name = properties.get('name', '')
        feature_type = ''
        
        if properties.get('building'):
            feature_type = 'building'
            if properties.get('building') != 'yes':
                feature_type = properties.get('building')
        elif properties.get('highway'):
            if properties.get('highway') == 'bus_stop':
                feature_type = 'bus stop'
            elif properties.get('highway') == 'bus_guideway':
                feature_type = 'bus guideway'
            else:
                feature_type = 'road'
        elif properties.get('amenity'):
            feature_type = properties.get('amenity').replace('_', ' ')
        elif properties.get('healthcare'):
            feature_type = properties.get('healthcare').replace('_', ' ')
        elif properties.get('railway'):
            if properties.get('railway') == 'subway_entrance':
                feature_type = 'subway entrance'
            elif properties.get('railway') == 'tram_stop':
                feature_type = 'tram stop'
            elif properties.get('railway') == 'light_rail':
                feature_type = 'light rail'
            elif properties.get('railway') == 'narrow_gauge':
                feature_type = 'narrow gauge railway'
            else:
                feature_type = properties.get('railway').replace('_', ' ')
        elif properties.get('public_transport'):
            if properties.get('public_transport') == 'stop_position':
                feature_type = 'transit stop'
            else:
                feature_type = properties.get('public_transport').replace('_', ' ')
        elif properties.get('aerialway'):
            if properties.get('aerialway') == 'cable_car':
                feature_type = 'cable car'
            elif properties.get('aerialway') == 'chair_lift':
                feature_type = 'chair lift'
            elif properties.get('aerialway') == 'drag_lift':
                feature_type = 'drag lift'
            elif properties.get('aerialway') == 'rope_tow':
                feature_type = 'rope tow'
            elif properties.get('aerialway') == 'zip_line':
                feature_type = 'zip line'
            elif properties.get('aerialway') == 'loading_point':
                feature_type = 'loading point'
            else:
                feature_type = properties.get('aerialway').replace('_', ' ')
        elif properties.get('aeroway'):
            feature_type = properties.get('aeroway').replace('_', ' ')
        elif properties.get('leisure'):
            feature_type = properties.get('leisure').replace('_', ' ')
        elif properties.get('natural'):
            feature_type = properties.get('natural').replace('_', ' ')
        
        if name and feature_type:
            return f"{name}, {feature_type}"
        elif name:
            return name
        elif feature_type:
            return feature_type.title()
        else:
            return "Map feature"
    
    def generate_svg_styles(self):
        """Generate CSS styles for SVG elements."""
        return """
        .feature-group { pointer-events: all; }
        .buildings polygon { opacity: 0.8; }
        .roads path { stroke-linecap: round; stroke-linejoin: round; }
        .water polygon, .water path { opacity: 0.7; }
        .parks polygon { opacity: 0.6; }
        .transit circle { opacity: 0.9; }
        """
    
    def store_tile_metadata(self, tile_lat, tile_lng, region_name, tile_file):
        """Store tile metadata in database."""
        # This would store metadata in SQLite database
        # Implementation will be added when we create the database module
        pass
    
    def update_region_metadata(self, region_name, bounds, tile_count):
        """Update region metadata file."""
        region_dir = self.tiles_dir / 'regions' / region_name
        metadata_file = region_dir / 'metadata.json'
        
        metadata = {
            'name': region_name,
            'bounds': bounds,
            'tile_count': tile_count,
            'created_at': datetime.now().isoformat(),
            'tile_size_degrees': self.tile_size,
            'svg_size': self.svg_size
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_generation_progress(self):
        """Get current generation progress for admin UI."""
        return self.current_progress.copy()
    
    def get_available_regions(self):
        """Get list of available regions."""
        regions = []
        regions_dir = self.tiles_dir / 'regions'
        
        if regions_dir.exists():
            for region_dir in regions_dir.iterdir():
                if region_dir.is_dir():
                    metadata_file = region_dir / 'metadata.json'
                    if metadata_file.exists():
                        try:
                            with open(metadata_file) as f:
                                metadata = json.load(f)
                                regions.append(metadata)
                        except Exception as e:
                            print(f"Error reading metadata for {region_dir.name}: {e}")
        
        return regions