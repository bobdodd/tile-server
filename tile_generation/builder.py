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
        
        # Region to province mapping
        self.region_to_province = {
            'toronto-downtown': 'ontario',
            'vancouver-downtown': 'british-columbia', 
            'calgary-downtown': 'alberta',
            'ottawa-downtown': 'ontario',
            'montreal-downtown': 'quebec'
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
            estimated_minutes = len(tiles_to_generate) * 4  # Estimate 4 minutes per tile
            print(f"⏱️  Estimated completion time: {estimated_minutes} minutes ({estimated_minutes/60:.1f} hours)")
            print(f"💡 Each tile processes the full OSM file - this is why it's slow")
            
            # Get cached OSM data for region (with optional pre-filtering)
            try:
                osm_file = self.get_region_osm_file(region_name, bounds)
            except FileNotFoundError as e:
                print(f"Error: {e}")
                raise Exception(f"OSM data not cached for region {region_name}. Please update OSM data first.")
            
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
    
    def get_region_osm_file(self, region_name, bounds=None):
        """Get the OSM file for a region, with optional pre-filtering for efficiency."""
        province = self.region_to_province.get(region_name, 'ontario')  # Default to Ontario
        cache_file = self.data_dir / 'osm_cache' / f"{province}-latest.osm.pbf"
        
        if not cache_file.exists():
            raise FileNotFoundError(f"No cached OSM data found for {province}. Please update OSM data first.")
        
        # Check if we have a pre-filtered regional file
        if bounds:
            regional_cache_file = self.data_dir / 'osm_cache' / f"{region_name}-filtered.osm.pbf"
            
            # Create regional filter if it doesn't exist or is older than main cache
            if (not regional_cache_file.exists() or 
                regional_cache_file.stat().st_mtime < cache_file.stat().st_mtime):
                
                print(f"Creating filtered OSM data for {region_name} to improve performance...")
                success = self.create_regional_filter(cache_file, regional_cache_file, bounds)
                
                if success:
                    print(f"Using filtered {region_name} OSM data: {regional_cache_file}")
                    return regional_cache_file
                else:
                    print(f"Filter creation failed, using full {province} OSM data: {cache_file}")
                    return cache_file
            else:
                print(f"Using cached filtered {region_name} OSM data: {regional_cache_file}")
                return regional_cache_file
        else:
            print(f"Using cached {province} OSM data: {cache_file}")
            return cache_file
    
    def download_region_data(self, region_name, bounds=None, force_update=False):
        """Download OSM data for the region using Geofabrik extracts."""
        # Map regions to their province/territory for Geofabrik downloads
        region_to_province = {
            'toronto-downtown': 'ontario',
            'vancouver-downtown': 'british-columbia', 
            'calgary-downtown': 'alberta',
            'ottawa-downtown': 'ontario',
            'montreal-downtown': 'quebec'
        }
        
        province = region_to_province.get(region_name, 'ontario')  # Default to Ontario
        cache_file = self.data_dir / 'osm_cache' / f"{province}-latest.osm.pbf"
        
        if cache_file.exists() and not force_update:
            # Check if cache is recent (within 28 days)
            cache_age = datetime.now().timestamp() - cache_file.stat().st_mtime
            if cache_age < 2419200:  # 28 days (28 * 24 * 3600)
                print(f"Using cached {province} OSM data: {cache_file}")
                return cache_file
        
        print(f"Downloading {province} OSM data from Geofabrik (includes {region_name})...")
        
        # Geofabrik download URL
        url = f"https://download.geofabrik.de/north-america/canada/{province}-latest.osm.pbf"
        
        try:
            print(f"Downloading from {url}...")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get file size for progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            print(f"Downloading {total_size / (1024*1024):.1f}MB...")
            
            with open(cache_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}% ({downloaded / (1024*1024):.1f}MB)", end='')
            
            print(f"\n✅ Downloaded and cached {province} OSM data: {cache_file}")
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
            try:
                print(f"  Processing OSM data for tile {tile_lat:.3f}, {tile_lng:.3f} (this may take several minutes for large files)")
                
                # Update progress to show OSM processing status
                self.current_progress['status'] = 'processing_osm'
                self.current_progress['current_tile'] = f"{tile_lat:.3f}_{tile_lng:.3f} (processing OSM data)"
                
                handler.apply_file(str(osm_file), locations=True)
                
                # Update progress to show tile rendering status
                self.current_progress['status'] = 'rendering_tile'
                self.current_progress['current_tile'] = f"{tile_lat:.3f}_{tile_lng:.3f} (rendering SVG)"
                
                print(f"  OSM processing complete for tile {tile_lat:.3f}, {tile_lng:.3f}")
            except Exception as osm_error:
                if "out of order" in str(osm_error):
                    print(f"OSM data sorting issue for tile {tile_lat:.3f}, {tile_lng:.3f}: {osm_error}")
                    print("This may be due to unsorted Overpass API data. Consider clearing cache.")
                raise osm_error
            
            # Create SVG content
            svg_content = self.create_tile_svg(tile_lat, tile_lng, handler.features, bounds)
            
            # Save compressed tile
            tile_filename = f"{tile_lat:.3f}_{tile_lng:.3f}.svg.gz"
            tile_path = self.tiles_dir / 'regions' / region_name / tile_filename
            
            with gzip.open(tile_path, 'wt', encoding='utf-8') as f:
                f.write(svg_content)
            
            return tile_path
            
        except Exception as e:
            print(f"Failed to generate tile {tile_lat:.3f}, {tile_lng:.3f}: {e}")
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
        
        # Add title element for hover tooltips
        title_text = self.generate_aria_label(properties)
        title_elem = Element('title')
        title_elem.text = title_text
        circle.insert(0, title_elem)  # Insert as first child
        
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
            
            # Add title element to the group for hover tooltips
            title_text = self.generate_aria_label(properties)
            title_elem = Element('title')
            title_elem.text = title_text
            group.insert(0, title_elem)  # Insert as first child
            
            return group
        
        # Add title element for roads without casing
        title_text = self.generate_aria_label(properties)
        title_elem = Element('title')
        title_elem.text = title_text
        path.insert(0, title_elem)  # Insert as first child
        
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
        
        # Add title element for hover tooltips
        title_text = self.generate_aria_label(properties)
        title_elem = Element('title')
        title_elem.text = title_text
        polygon.insert(0, title_elem)  # Insert as first child
        
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
            # Linear Water Features (waterway)
            if properties.get('waterway'):
                return properties.get('waterway')
            # Large Water Bodies (natural)
            elif properties.get('natural') in ['water', 'bay', 'strait', 'coastline', 'beach', 'shoal', 'reef', 'wetland', 'spring', 'hot_spring', 'geyser']:
                return properties.get('natural')
            # Man-made Water Features (man_made)
            elif properties.get('man_made') in ['reservoir', 'water_tower', 'water_well', 'water_works', 'pier', 'breakwater', 'groyne', 'lighthouse', 'floating_dock']:
                return properties.get('man_made')
            # Amenity Water Features
            elif properties.get('amenity') == 'fountain':
                return 'fountain'
            elif properties.get('amenity') == 'swimming_pool':
                return 'swimming_pool'
            # Leisure Water Features
            elif properties.get('leisure') in ['swimming_pool', 'water_park', 'marina', 'slipway', 'boat_sharing']:
                return properties.get('leisure')
            # Landuse Water Areas
            elif properties.get('landuse') in ['reservoir', 'salt_pond', 'aquaculture', 'basin']:
                return properties.get('landuse')
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
        elif feature_type == 'historic_cultural':
            # Historic sites
            if properties.get('historic'):
                return properties.get('historic')
            # Tourism & cultural attractions
            elif properties.get('tourism') in ['museum', 'gallery', 'artwork', 'attraction', 'theme_park']:
                return properties.get('tourism')
            # Cultural centers
            elif properties.get('cultural'):
                return properties.get('cultural')
            # Cemetery/burial sites
            elif properties.get('amenity') == 'grave_yard':
                return 'grave_yard'
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
        elif properties.get('shop'):
            # Shop/retail establishments
            if properties.get('shop') == 'department_store':
                feature_type = 'department store'
            elif properties.get('shop') == 'convenience':
                feature_type = 'convenience store'
            elif properties.get('shop') == 'mobile_phone':
                feature_type = 'mobile phone store'
            elif properties.get('shop') == 'garden_centre':
                feature_type = 'garden centre'
            elif properties.get('shop') == 'second_hand':
                feature_type = 'second hand store'
            else:
                feature_type = properties.get('shop').replace('_', ' ')
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
        elif properties.get('man_made'):
            if properties.get('man_made') == 'water_tower':
                feature_type = 'water tower'
            elif properties.get('man_made') == 'water_well':
                feature_type = 'water well'
            elif properties.get('man_made') == 'water_works':
                feature_type = 'water treatment plant'
            elif properties.get('man_made') == 'hot_spring':
                feature_type = 'hot spring'
            elif properties.get('man_made') == 'floating_dock':
                feature_type = 'floating dock'
            else:
                feature_type = properties.get('man_made').replace('_', ' ')
        elif properties.get('waterway'):
            feature_type = properties.get('waterway').replace('_', ' ')
        elif properties.get('leisure'):
            if properties.get('leisure') == 'water_park':
                feature_type = 'water park'
            elif properties.get('leisure') == 'boat_sharing':
                feature_type = 'boat sharing station'
            else:
                feature_type = properties.get('leisure').replace('_', ' ')
        elif properties.get('natural'):
            if properties.get('natural') == 'hot_spring':
                feature_type = 'hot spring'
            else:
                feature_type = properties.get('natural').replace('_', ' ')
        elif properties.get('landuse'):
            if properties.get('landuse') == 'salt_pond':
                feature_type = 'salt pond'
            else:
                feature_type = properties.get('landuse').replace('_', ' ')
        elif properties.get('historic'):
            # Historic sites with specific labels
            if properties.get('historic') == 'archaeological_site':
                feature_type = 'archaeological site'
            elif properties.get('historic') == 'wayside_cross':
                feature_type = 'wayside cross'
            elif properties.get('historic') == 'wayside_shrine':
                feature_type = 'wayside shrine'
            elif properties.get('historic') == 'blue_plaque':
                feature_type = 'blue plaque'
            elif properties.get('historic') == 'ghost_sign':
                feature_type = 'ghost sign'
            elif properties.get('historic') == 'optical_telegraph':
                feature_type = 'optical telegraph'
            elif properties.get('historic') == 'highwater_mark':
                feature_type = 'high water mark'
            elif properties.get('historic') == 'pa_system':
                feature_type = 'PA system'
            elif properties.get('historic') == 'boundary_stone':
                feature_type = 'boundary stone'
            elif properties.get('historic') == 'railway_car':
                feature_type = 'historic railway car'
            else:
                feature_type = properties.get('historic').replace('_', ' ')
        elif properties.get('tourism') in ['museum', 'gallery', 'artwork', 'attraction', 'theme_park']:
            if properties.get('tourism') == 'theme_park':
                feature_type = 'theme park'
            else:
                feature_type = properties.get('tourism')
        elif properties.get('cultural'):
            if properties.get('cultural') == 'cultural_centre':
                feature_type = 'cultural centre'
            elif properties.get('cultural') == 'arts_centre':
                feature_type = 'arts centre'
            elif properties.get('cultural') == 'community_centre':
                feature_type = 'community centre'
            else:
                feature_type = properties.get('cultural').replace('_', ' ')
        elif properties.get('emergency'):
            # Emergency services and equipment
            if properties.get('emergency') == 'fire_hydrant':
                feature_type = 'fire hydrant'
            elif properties.get('emergency') == 'defibrillator':
                feature_type = 'defibrillator'
            elif properties.get('emergency') == 'phone':
                feature_type = 'emergency phone'
            else:
                feature_type = properties.get('emergency').replace('_', ' ')
        elif properties.get('barrier'):
            # Barriers and access control
            if properties.get('barrier') == 'lift_gate':
                feature_type = 'lift gate'
            elif properties.get('barrier') == 'toll_booth':
                feature_type = 'toll booth'
            elif properties.get('barrier') == 'swing_gate':
                feature_type = 'swing gate'
            elif properties.get('barrier') == 'jersey_barrier':
                feature_type = 'jersey barrier'
            else:
                feature_type = properties.get('barrier').replace('_', ' ')
        elif properties.get('information'):
            # Tourism information (more specific than the general tourism check)
            if properties.get('information') == 'guidepost':
                feature_type = 'guidepost'
            elif properties.get('information') == 'map':
                feature_type = 'information map'
            else:
                feature_type = f"information {properties.get('information')}"
        
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
    
    def get_osm_cache_status(self):
        """Get status of all cached OSM data files."""
        cache_status = {}
        
        for region_name, province in self.region_to_province.items():
            cache_file = self.data_dir / 'osm_cache' / f"{province}-latest.osm.pbf"
            
            if cache_file.exists():
                stat = cache_file.stat()
                cache_age = datetime.now().timestamp() - stat.st_mtime
                size_mb = stat.st_size / (1024 * 1024)
                
                cache_status[province] = {
                    'exists': True,
                    'file_path': str(cache_file),
                    'size_mb': round(size_mb, 1),
                    'age_hours': round(cache_age / 3600, 1),
                    'age_days': round(cache_age / 86400, 1),
                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'is_fresh': cache_age < 2419200,  # Fresh if less than 28 days old
                    'regions': [r for r, p in self.region_to_province.items() if p == province]
                }
            else:
                cache_status[province] = {
                    'exists': False,
                    'file_path': str(cache_file),
                    'size_mb': 0,
                    'age_hours': 0,
                    'age_days': 0,
                    'last_modified': None,
                    'is_fresh': False,
                    'regions': [r for r, p in self.region_to_province.items() if p == province]
                }
        
        return cache_status
    
    def update_osm_data(self, province=None, force=True):
        """Update OSM data for a specific province or all provinces."""
        results = {}
        
        if province:
            # Update specific province
            provinces_to_update = [province]
        else:
            # Update all provinces that have associated regions
            provinces_to_update = list(set(self.region_to_province.values()))
        
        for prov in provinces_to_update:
            try:
                # Find a region that uses this province
                region_name = next(r for r, p in self.region_to_province.items() if p == prov)
                cache_file = self.download_region_data(region_name, force_update=force)
                results[prov] = {
                    'success': True,
                    'file_path': str(cache_file),
                    'message': f'Successfully updated {prov} OSM data'
                }
            except Exception as e:
                results[prov] = {
                    'success': False,
                    'file_path': None,
                    'message': f'Failed to update {prov}: {str(e)}'
                }
        
        return results
    
    def create_regional_filter(self, source_file, output_file, bounds):
        """Create a filtered OSM file for a specific region to improve processing speed."""
        try:
            # Add small buffer to bounds to ensure we don't miss edge features
            buffer = 0.005  # About 500m buffer
            
            bbox = f"{bounds['west'] - buffer},{bounds['south'] - buffer},{bounds['east'] + buffer},{bounds['north'] + buffer}"
            
            # Use osmium extract command if available
            import subprocess
            import shutil
            
            # Check if osmium is available as command line tool
            if shutil.which('osmium'):
                cmd = [
                    'osmium', 'extract', 
                    '--bbox', bbox,
                    '--output', str(output_file),
                    str(source_file)
                ]
                
                print(f"  Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minute timeout
                
                if result.returncode == 0:
                    # Check if output file was created and has reasonable size
                    if output_file.exists() and output_file.stat().st_size > 1000:  # At least 1KB
                        size_mb = output_file.stat().st_size / (1024 * 1024)
                        print(f"  ✅ Created filtered OSM file: {size_mb:.1f}MB (was {source_file.stat().st_size / (1024 * 1024):.0f}MB)")
                        return True
                    else:
                        print(f"  ❌ Filtered file too small or missing")
                        if output_file.exists():
                            output_file.unlink()
                        return False
                else:
                    print(f"  ❌ osmium extract failed: {result.stderr}")
                    return False
            else:
                print(f"  ❌ osmium command line tool not available, using full province file")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"  ❌ osmium extract timed out after 5 minutes")
            if output_file.exists():
                output_file.unlink()
            return False
        except Exception as e:
            print(f"  ❌ Error creating regional filter: {e}")
            if output_file.exists():
                output_file.unlink()
            return False