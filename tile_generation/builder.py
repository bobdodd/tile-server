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
        elif feature_type == 'craft_specialized_services':
            return properties.get('craft', 'default')
        elif feature_type == 'communication_technology':
            # Determine communication/tech subtype based on tags
            if properties.get('amenity') in ['post_box', 'telephone']:
                return properties.get('amenity')
            elif properties.get('telecom') == 'data_center':
                return 'data_center'
            elif properties.get('communication') == 'line':
                return 'line'
            return 'default'
        elif feature_type == 'education_childcare':
            # Determine education/childcare subtype
            return properties.get('amenity', 'default')
        elif feature_type == 'sports_fitness':
            # Determine sports/fitness subtype - prefer sport tag, fallback to leisure
            if properties.get('sport'):
                return properties.get('sport')
            elif properties.get('leisure'):
                return properties.get('leisure')
            return 'default'
        
        elif feature_type == 'agricultural_rural':
            # Determine agricultural/rural subtype - prefer specific tags over generic ones
            if properties.get('landuse'):
                return properties.get('landuse')
            elif properties.get('building'):
                return properties.get('building')
            elif properties.get('man_made'):
                return properties.get('man_made')
            elif properties.get('craft'):
                return properties.get('craft')
            elif properties.get('shop'):
                return properties.get('shop')
            elif properties.get('amenity'):
                return properties.get('amenity')
            elif properties.get('leisure'):
                return properties.get('leisure')
            elif properties.get('natural'):
                return properties.get('natural')
            elif properties.get('agriculture'):
                return properties.get('agriculture')
            elif properties.get('produce'):
                return properties.get('produce')
            return 'default'
        
        elif feature_type == 'military_government':
            # Determine military/government subtype - prefer specific tags over generic ones
            if properties.get('military'):
                return properties.get('military')
            elif properties.get('government'):
                return properties.get('government')
            elif properties.get('amenity'):
                return properties.get('amenity')
            elif properties.get('building'):
                return properties.get('building')
            elif properties.get('office'):
                return properties.get('office')
            elif properties.get('diplomatic'):
                return properties.get('diplomatic')
            elif properties.get('public_service'):
                return properties.get('public_service')
            elif properties.get('landuse'):
                return properties.get('landuse')
            return 'default'
        
        elif feature_type == 'leisure_entertainment_details':
            # Determine leisure/entertainment subtype - prefer specific tags over generic ones
            if properties.get('leisure'):
                return properties.get('leisure')
            elif properties.get('amenity'):
                return properties.get('amenity')
            elif properties.get('shop'):
                return properties.get('shop')
            elif properties.get('club'):
                return properties.get('club')
            elif properties.get('tourism'):
                return properties.get('tourism')
            elif properties.get('sport'):
                return properties.get('sport')
            elif properties.get('craft'):
                return properties.get('craft')
            elif properties.get('entertainment'):
                return properties.get('entertainment')
            return 'default'
        
        elif feature_type == 'sensory_accessibility':
            # Determine sensory accessibility subtype based on specific accessibility features
            if properties.get('tactile_paving') == 'yes':
                return 'tactile_paving_yes'
            elif properties.get('tactile_paving') == 'no':
                return 'tactile_paving_no'
            elif properties.get('traffic_signals:sound') == 'yes':
                return 'traffic_signals_sound'
            elif properties.get('traffic_signals:vibration') == 'yes':
                return 'traffic_signals_vibration'
            elif properties.get('acoustic') == 'voice_description':
                return 'acoustic_voice'
            elif properties.get('braille') == 'yes':
                return 'braille'
            elif properties.get('audio_loop') == 'yes':
                return 'audio_loop'
            elif properties.get('sign_language') == 'yes':
                return 'sign_language'
            return 'default'
        
        elif feature_type == 'accessible_facilities':
            # Determine accessible facility subtype based on facility type and accessibility
            if properties.get('toilets:wheelchair') == 'yes':
                return 'toilets_wheelchair_yes'
            elif properties.get('toilets:wheelchair') == 'no':
                return 'toilets_wheelchair_no'
            elif properties.get('changing_table') == 'yes':
                return 'changing_table_yes'
            elif properties.get('changing_table') == 'no':
                return 'changing_table_no'
            elif properties.get('elevator') == 'yes':
                return 'elevator_yes'
            elif properties.get('elevator') == 'no':
                return 'elevator_no'
            elif properties.get('highway') == 'elevator':
                return 'elevator'
            elif properties.get('escalator') == 'yes':
                return 'escalator_yes'
            elif properties.get('escalator') == 'no':
                return 'escalator_no'
            elif properties.get('highway') == 'escalator':
                return 'escalator'
            elif properties.get('conveying') == 'yes':
                return 'conveying_yes'
            elif properties.get('conveying') == 'no':
                return 'conveying_no'
            elif properties.get('automatic_door') == 'yes':
                return 'automatic_door_yes'
            elif properties.get('automatic_door') == 'no':
                return 'automatic_door_no'
            elif 'door:width' in properties:
                return 'door_width'
            elif 'kerb:height' in properties:
                return 'kerb_height'
            elif 'incline' in properties:
                return 'incline'
            return 'default'
        
        elif feature_type == 'mobility_access':
            # Determine mobility access subtype based on accessibility features
            if properties.get('wheelchair') == 'yes':
                return 'wheelchair_yes'
            elif properties.get('wheelchair') == 'no':
                return 'wheelchair_no'
            elif properties.get('wheelchair') == 'limited':
                return 'wheelchair_limited'
            elif properties.get('wheelchair') == 'designated':
                return 'wheelchair_designated'
            elif properties.get('ramp') == 'yes':
                return 'ramp_yes'
            elif properties.get('ramp') == 'no':
                return 'ramp_no'
            elif properties.get('ramp:wheelchair') == 'yes':
                return 'ramp_wheelchair_yes'
            elif properties.get('ramp:wheelchair') == 'no':
                return 'ramp_wheelchair_no'
            elif properties.get('ramp:stroller') == 'yes':
                return 'ramp_stroller_yes'
            elif properties.get('ramp:stroller') == 'no':
                return 'ramp_stroller_no'
            elif properties.get('ramp:bicycle') == 'yes':
                return 'ramp_bicycle_yes'
            elif properties.get('ramp:bicycle') == 'no':
                return 'ramp_bicycle_no'
            elif 'step_count' in properties:
                return 'step_count'
            elif properties.get('handrail') == 'yes':
                return 'handrail_yes'
            elif properties.get('handrail') == 'no':
                return 'handrail_no'
            elif properties.get('handrail:center') == 'yes':
                return 'handrail_center'
            elif properties.get('handrail:left') == 'yes':
                return 'handrail_left'
            elif properties.get('handrail:right') == 'yes':
                return 'handrail_right'
            return 'default'
        
        elif feature_type == 'accessible_transport':
            # Determine accessible transport subtype based on transport accessibility
            if properties.get('parking:disabled') == 'yes':
                return 'parking_disabled_yes'
            elif properties.get('parking:disabled') == 'no':
                return 'parking_disabled_no'
            elif properties.get('priority') == 'disabled':
                return 'priority_disabled'
            elif 'capacity:disabled' in properties:
                return 'capacity_disabled'
            elif properties.get('bus:wheelchair') == 'yes':
                return 'bus_wheelchair_yes'
            elif properties.get('bus:wheelchair') == 'no':
                return 'bus_wheelchair_no'
            elif properties.get('subway:wheelchair') == 'yes':
                return 'subway_wheelchair_yes'
            elif properties.get('subway:wheelchair') == 'no':
                return 'subway_wheelchair_no'
            elif properties.get('tram:wheelchair') == 'yes':
                return 'tram_wheelchair_yes'
            elif properties.get('tram:wheelchair') == 'no':
                return 'tram_wheelchair_no'
            elif properties.get('train:wheelchair') == 'yes':
                return 'train_wheelchair_yes'
            elif properties.get('train:wheelchair') == 'no':
                return 'train_wheelchair_no'
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
        elif properties.get('amenity') in ['childcare', 'language_school', 'driving_school', 'music_school', 'research_institute']:
            # Education and childcare facilities (handle before generic amenity)
            if properties.get('amenity') == 'childcare':
                feature_type = 'childcare center'
            elif properties.get('amenity') == 'language_school':
                feature_type = 'language school'
            elif properties.get('amenity') == 'driving_school':
                feature_type = 'driving school'
            elif properties.get('amenity') == 'music_school':
                feature_type = 'music school'
            elif properties.get('amenity') == 'research_institute':
                feature_type = 'research institute'
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
        elif properties.get('leisure') in ['fitness_station', 'track', 'pitch', 'marina', 'slipway'] or properties.get('sport'):
            # Sports and fitness facilities (handle before generic leisure)
            if properties.get('sport'):
                sport_type = properties.get('sport')
                # Ball sports
                if sport_type == 'tennis':
                    feature_type = 'tennis court'
                elif sport_type in ['football', 'soccer']:
                    feature_type = 'football field'
                elif sport_type == 'basketball':
                    feature_type = 'basketball court'
                elif sport_type == 'volleyball':
                    feature_type = 'volleyball court'
                elif sport_type == 'baseball':
                    feature_type = 'baseball field'
                elif sport_type == 'hockey':
                    feature_type = 'hockey rink'
                # Racket sports
                elif sport_type == 'table_tennis':
                    feature_type = 'table tennis facility'
                elif sport_type == 'badminton':
                    feature_type = 'badminton court'
                elif sport_type == 'squash':
                    feature_type = 'squash court'
                # Water sports
                elif sport_type == 'swimming':
                    feature_type = 'swimming facility'
                elif sport_type == 'sailing':
                    feature_type = 'sailing facility'
                elif sport_type == 'rowing':
                    feature_type = 'rowing facility'
                elif sport_type == 'canoe':
                    feature_type = 'canoe facility'
                elif sport_type == 'surfing':
                    feature_type = 'surfing area'
                # Individual sports
                elif sport_type == 'athletics':
                    feature_type = 'athletics track'
                elif sport_type == 'running':
                    feature_type = 'running track'
                elif sport_type == 'cycling':
                    feature_type = 'cycling track'
                elif sport_type == 'golf':
                    feature_type = 'golf course'
                # Fitness & wellness
                elif sport_type == 'fitness':
                    feature_type = 'fitness center'
                elif sport_type == 'gym':
                    feature_type = 'gymnasium'
                elif sport_type == 'yoga':
                    feature_type = 'yoga studio'
                elif sport_type == 'dance':
                    feature_type = 'dance studio'
                # Combat sports
                elif sport_type == 'boxing':
                    feature_type = 'boxing gym'
                elif sport_type == 'martial_arts':
                    feature_type = 'martial arts facility'
                # Adventure sports
                elif sport_type == 'climbing':
                    feature_type = 'climbing facility'
                elif sport_type == 'equestrian':
                    feature_type = 'equestrian facility'
                # Urban sports
                elif sport_type == 'skateboard':
                    feature_type = 'skateboard park'
                elif sport_type == 'bmx':
                    feature_type = 'BMX track'
                else:
                    feature_type = f"{sport_type.replace('_', ' ')} facility"
            elif properties.get('leisure') == 'fitness_station':
                feature_type = 'fitness station'
            elif properties.get('leisure') == 'track':
                feature_type = 'running track'
            elif properties.get('leisure') == 'pitch':
                feature_type = 'sports field'
            elif properties.get('leisure') == 'marina':
                feature_type = 'marina'
            elif properties.get('leisure') == 'slipway':
                feature_type = 'boat launch'
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
        elif properties.get('craft'):
            # Craft and specialized services
            craft_type = properties.get('craft').replace('_', ' ')
            feature_type = f"{craft_type} workshop"
        elif properties.get('amenity') in ['post_box', 'telephone']:
            # Communication amenities
            if properties.get('amenity') == 'post_box':
                feature_type = 'post box'
            elif properties.get('amenity') == 'telephone':
                feature_type = 'public telephone'
        elif properties.get('telecom') == 'data_center':
            feature_type = 'data center'
        elif properties.get('communication') == 'line':
            feature_type = 'communication line'
        
        # Agricultural & Rural Features - Comprehensive agricultural and rural facility labeling
        elif (properties.get('landuse') in ['orchard', 'vineyard', 'allotments', 'farmyard', 'farmland', 'animal_keeping', 'plant_nursery', 'greenhouse_horticulture', 'aquaculture'] or
              properties.get('man_made') in ['silo', 'storage_tank', 'bunker_silo', 'windmill', 'watermill', 'windpump', 'watering_place'] or
              properties.get('building') in ['farm_auxiliary', 'barn', 'stable', 'sty', 'greenhouse', 'cowshed', 'chicken_coop', 'farm'] or
              properties.get('amenity') in ['animal_shelter', 'animal_boarding', 'veterinary'] or
              properties.get('craft') in ['agricultural_engines', 'beekeeper', 'distillery', 'winery'] or
              properties.get('shop') in ['farm', 'garden_centre', 'agrarian', 'feed'] or
              properties.get('leisure') in ['fishing', 'garden'] or
              properties.get('agriculture') in ['greenhouse', 'crop', 'livestock', 'dairy', 'poultry', 'beekeeping'] or
              properties.get('produce') in ['fruit', 'vegetable', 'grain', 'dairy', 'meat', 'eggs', 'honey']):
            
            # Agricultural land use
            if properties.get('landuse') == 'orchard':
                feature_type = 'orchard'
            elif properties.get('landuse') == 'vineyard':
                feature_type = 'vineyard'
            elif properties.get('landuse') == 'allotments':
                feature_type = 'community garden'
            elif properties.get('landuse') == 'farmyard':
                feature_type = 'farmyard'
            elif properties.get('landuse') == 'farmland':
                feature_type = 'farmland'
            elif properties.get('landuse') == 'animal_keeping':
                feature_type = 'animal keeping area'
            elif properties.get('landuse') == 'plant_nursery':
                feature_type = 'plant nursery'
            elif properties.get('landuse') == 'greenhouse_horticulture':
                feature_type = 'greenhouse complex'
            elif properties.get('landuse') == 'aquaculture':
                feature_type = 'fish farm'
            
            # Agricultural buildings
            elif properties.get('building') == 'barn':
                feature_type = 'barn'
            elif properties.get('building') == 'farm_auxiliary':
                feature_type = 'farm building'
            elif properties.get('building') == 'farm':
                feature_type = 'farmhouse'
            elif properties.get('building') == 'stable':
                feature_type = 'stable'
            elif properties.get('building') == 'sty':
                feature_type = 'pig pen'
            elif properties.get('building') == 'greenhouse':
                feature_type = 'greenhouse'
            elif properties.get('building') == 'cowshed':
                feature_type = 'cow shed'
            elif properties.get('building') == 'chicken_coop':
                feature_type = 'chicken coop'
            
            # Agricultural infrastructure
            elif properties.get('man_made') == 'silo':
                feature_type = 'grain silo'
            elif properties.get('man_made') == 'storage_tank':
                feature_type = 'storage tank'
            elif properties.get('man_made') == 'bunker_silo':
                feature_type = 'bunker silo'
            elif properties.get('man_made') == 'windmill':
                feature_type = 'windmill'
            elif properties.get('man_made') == 'watermill':
                feature_type = 'water mill'
            elif properties.get('man_made') == 'windpump':
                feature_type = 'wind pump'
            elif properties.get('man_made') == 'watering_place':
                feature_type = 'watering place'
            
            # Agricultural crafts and services
            elif properties.get('craft') == 'agricultural_engines':
                feature_type = 'agricultural equipment shop'
            elif properties.get('craft') == 'beekeeper':
                feature_type = 'beekeeping facility'
            elif properties.get('craft') == 'distillery':
                feature_type = 'distillery'
            elif properties.get('craft') == 'winery':
                feature_type = 'winery'
            
            # Agricultural retail
            elif properties.get('shop') == 'farm':
                feature_type = 'farm shop'
            elif properties.get('shop') == 'garden_centre':
                feature_type = 'garden center'
            elif properties.get('shop') == 'agrarian':
                feature_type = 'agricultural supply store'
            elif properties.get('shop') == 'feed':
                feature_type = 'feed store'
            
            # Animal services
            elif properties.get('amenity') == 'animal_shelter':
                feature_type = 'animal shelter'
            elif properties.get('amenity') == 'animal_boarding':
                feature_type = 'animal boarding facility'
            elif properties.get('amenity') == 'veterinary':
                feature_type = 'veterinary clinic'
            
            # Rural recreation
            elif properties.get('leisure') == 'fishing':
                feature_type = 'fishing area'
            elif properties.get('leisure') == 'garden':
                feature_type = 'community garden'
            
            # Agricultural production
            elif properties.get('agriculture') == 'greenhouse':
                feature_type = 'greenhouse operation'
            elif properties.get('agriculture') == 'crop':
                feature_type = 'crop production'
            elif properties.get('agriculture') == 'livestock':
                feature_type = 'livestock farm'
            elif properties.get('agriculture') == 'dairy':
                feature_type = 'dairy farm'
            elif properties.get('agriculture') == 'poultry':
                feature_type = 'poultry farm'
            elif properties.get('agriculture') == 'beekeeping':
                feature_type = 'apiary'
            
            # Agricultural produce
            elif properties.get('produce') == 'fruit':
                feature_type = 'fruit production'
            elif properties.get('produce') == 'vegetable':
                feature_type = 'vegetable production'
            elif properties.get('produce') == 'grain':
                feature_type = 'grain production'
            elif properties.get('produce') == 'dairy':
                feature_type = 'dairy production'
            elif properties.get('produce') == 'meat':
                feature_type = 'meat production'
            elif properties.get('produce') == 'eggs':
                feature_type = 'egg production'
            elif properties.get('produce') == 'honey':
                feature_type = 'honey production'
        
        # Military & Government Features - Comprehensive military installation and government facility labeling
        elif (properties.get('military') in ['airfield', 'base', 'bunker', 'barracks', 'checkpoint', 'danger_area', 'nuclear_explosion_site', 'obstacle_course', 'office', 'range', 'training_area', 'naval_base', 'depot', 'academy', 'hospital'] or
              properties.get('government') in ['administrative', 'archive', 'courthouse', 'customs', 'diplomatic', 'embassy', 'fire_department', 'legislative', 'library', 'military', 'ministry', 'office', 'parliament', 'police', 'prison', 'public_service', 'register_office', 'social_services', 'taxation', 'town_hall'] or
              properties.get('amenity') in ['courthouse', 'prison', 'police', 'fire_station', 'embassy', 'townhall', 'customs', 'ranger_station'] or
              properties.get('building') in ['government', 'military', 'courthouse', 'prison', 'fire_station', 'police'] or
              properties.get('landuse') in ['military', 'government'] or
              properties.get('office') in ['government', 'diplomatic', 'administrative', 'military'] or
              properties.get('diplomatic') in ['embassy', 'consulate', 'delegation', 'mission'] or
              properties.get('public_service') in ['social_services', 'employment_agency', 'tax_office']):
            
            # Military installations
            if properties.get('military') == 'base':
                feature_type = 'military base'
            elif properties.get('military') == 'airfield':
                feature_type = 'military airfield'
            elif properties.get('military') == 'naval_base':
                feature_type = 'naval base'
            elif properties.get('military') == 'barracks':
                feature_type = 'military barracks'
            elif properties.get('military') == 'depot':
                feature_type = 'military depot'
            elif properties.get('military') == 'academy':
                feature_type = 'military academy'
            elif properties.get('military') == 'hospital':
                feature_type = 'military hospital'
            elif properties.get('military') == 'bunker':
                feature_type = 'military bunker'
            elif properties.get('military') == 'checkpoint':
                feature_type = 'security checkpoint'
            elif properties.get('military') == 'danger_area':
                feature_type = 'military danger area'
            elif properties.get('military') == 'nuclear_explosion_site':
                feature_type = 'nuclear test site'
            elif properties.get('military') == 'range':
                feature_type = 'firing range'
            elif properties.get('military') == 'training_area':
                feature_type = 'military training area'
            elif properties.get('military') == 'obstacle_course':
                feature_type = 'military obstacle course'
            elif properties.get('military') == 'office':
                feature_type = 'military office'
            
            # Government buildings
            elif properties.get('government') == 'courthouse':
                feature_type = 'courthouse'
            elif properties.get('government') == 'parliament':
                feature_type = 'parliament building'
            elif properties.get('government') == 'town_hall':
                feature_type = 'town hall'
            elif properties.get('government') == 'ministry':
                feature_type = 'government ministry'
            elif properties.get('government') == 'legislative':
                feature_type = 'legislative building'
            elif properties.get('government') == 'administrative':
                feature_type = 'government office'
            elif properties.get('government') == 'archive':
                feature_type = 'government archive'
            elif properties.get('government') == 'library':
                feature_type = 'government library'
            elif properties.get('government') == 'register_office':
                feature_type = 'registry office'
            elif properties.get('government') == 'taxation':
                feature_type = 'tax office'
            elif properties.get('government') == 'customs':
                feature_type = 'customs office'
            elif properties.get('government') == 'public_service':
                feature_type = 'public service office'
            elif properties.get('government') == 'social_services':
                feature_type = 'social services office'
            
            # Law enforcement and justice
            elif properties.get('government') == 'police':
                feature_type = 'police station'
            elif properties.get('amenity') == 'police':
                feature_type = 'police station'
            elif properties.get('government') == 'prison':
                feature_type = 'correctional facility'
            elif properties.get('amenity') == 'prison':
                feature_type = 'correctional facility'
            elif properties.get('amenity') == 'courthouse':
                feature_type = 'courthouse'
            
            # Emergency services
            elif properties.get('government') == 'fire_department':
                feature_type = 'fire department'
            elif properties.get('amenity') == 'fire_station':
                feature_type = 'fire station'
            elif properties.get('amenity') == 'ranger_station':
                feature_type = 'ranger station'
            
            # Diplomatic services
            elif properties.get('government') == 'embassy':
                feature_type = 'embassy'
            elif properties.get('amenity') == 'embassy':
                feature_type = 'embassy'
            elif properties.get('diplomatic') == 'embassy':
                feature_type = 'embassy'
            elif properties.get('diplomatic') == 'consulate':
                feature_type = 'consulate'
            elif properties.get('diplomatic') == 'delegation':
                feature_type = 'diplomatic delegation'
            elif properties.get('diplomatic') == 'mission':
                feature_type = 'diplomatic mission'
            
            # Government offices
            elif properties.get('office') == 'government':
                feature_type = 'government office'
            elif properties.get('office') == 'diplomatic':
                feature_type = 'diplomatic office'
            elif properties.get('office') == 'administrative':
                feature_type = 'administrative office'
            elif properties.get('office') == 'military':
                feature_type = 'military office'
            
            # Public services
            elif properties.get('public_service') == 'social_services':
                feature_type = 'social services office'
            elif properties.get('public_service') == 'employment_agency':
                feature_type = 'employment office'
            elif properties.get('public_service') == 'tax_office':
                feature_type = 'tax office'
            
            # Buildings and amenities
            elif properties.get('amenity') == 'townhall':
                feature_type = 'town hall'
            elif properties.get('amenity') == 'customs':
                feature_type = 'customs office'
            elif properties.get('building') == 'government':
                feature_type = 'government building'
            elif properties.get('building') == 'military':
                feature_type = 'military building'
            elif properties.get('building') == 'courthouse':
                feature_type = 'courthouse'
            elif properties.get('building') == 'prison':
                feature_type = 'correctional facility'
            elif properties.get('building') == 'fire_station':
                feature_type = 'fire station'
            elif properties.get('building') == 'police':
                feature_type = 'police station'
            
            # Land use
            elif properties.get('landuse') == 'military':
                feature_type = 'military area'
            elif properties.get('landuse') == 'government':
                feature_type = 'government area'
        
        # Leisure & Entertainment Details - Comprehensive leisure and entertainment venue labeling
        elif (properties.get('leisure') in ['dance', 'escape_game', 'hackerspace', 'adult_gaming_centre', 'miniature_golf', 'arcade', 'bingo_hall', 'casino', 'gambling', 'social_club', 'sauna', 'bandstand', 'bleachers', 'maze', 'shooting_range', 'disc_golf', 'picnic_table', 'firepit', 'bbq'] or
              properties.get('amenity') in ['casino', 'gambling', 'game_feeding', 'karaoke_box', 'love_hotel', 'nightclub', 'planetarium', 'social_facility', 'stripclub', 'swingerclub', 'brothel', 'studio'] or
              properties.get('shop') in ['games', 'lottery', 'video_games', 'music', 'musical_instrument', 'video', 'books', 'art', 'craft', 'hobby'] or
              properties.get('club') in ['sport', 'social', 'veterans', 'youth', 'senior', 'community', 'photography', 'computer', 'automobile'] or
              properties.get('tourism') in ['theme_park', 'aquarium', 'zoo'] or
              properties.get('sport') in ['billiards', 'darts', 'chess', 'go', 'beachvolleyball'] or
              properties.get('craft') in ['brewery', 'distillery', 'winery'] or
              properties.get('entertainment') in ['escape_room', 'laser_tag', 'paintball', 'axe_throwing', 'virtual_reality']):
            
            # Dance and performance venues
            if properties.get('leisure') == 'dance':
                feature_type = 'dance studio'
            elif properties.get('leisure') == 'bandstand':
                feature_type = 'bandstand'
            elif properties.get('amenity') == 'studio':
                feature_type = 'recording studio'
            
            # Gaming and entertainment venues
            elif properties.get('leisure') == 'escape_game':
                feature_type = 'escape room'
            elif properties.get('entertainment') == 'escape_room':
                feature_type = 'escape room'
            elif properties.get('leisure') == 'arcade':
                feature_type = 'arcade'
            elif properties.get('leisure') == 'adult_gaming_centre':
                feature_type = 'adult gaming center'
            elif properties.get('leisure') == 'bingo_hall':
                feature_type = 'bingo hall'
            elif properties.get('entertainment') == 'laser_tag':
                feature_type = 'laser tag arena'
            elif properties.get('entertainment') == 'paintball':
                feature_type = 'paintball field'
            elif properties.get('entertainment') == 'axe_throwing':
                feature_type = 'axe throwing venue'
            elif properties.get('entertainment') == 'virtual_reality':
                feature_type = 'VR arcade'
            
            # Gambling and casino venues
            elif properties.get('leisure') == 'casino':
                feature_type = 'casino'
            elif properties.get('amenity') == 'casino':
                feature_type = 'casino'
            elif properties.get('leisure') == 'gambling':
                feature_type = 'gambling venue'
            elif properties.get('amenity') == 'gambling':
                feature_type = 'gambling venue'
            elif properties.get('shop') == 'lottery':
                feature_type = 'lottery retailer'
            
            # Nightlife and social venues
            elif properties.get('amenity') == 'nightclub':
                feature_type = 'nightclub'
            elif properties.get('amenity') == 'karaoke_box':
                feature_type = 'karaoke venue'
            elif properties.get('leisure') == 'social_club':
                feature_type = 'social club'
            elif properties.get('amenity') == 'social_facility':
                feature_type = 'social facility'
            elif properties.get('amenity') == 'love_hotel':
                feature_type = 'love hotel'
            elif properties.get('amenity') == 'stripclub':
                feature_type = 'strip club'
            elif properties.get('amenity') == 'swingerclub':
                feature_type = 'swinger club'
            elif properties.get('amenity') == 'brothel':
                feature_type = 'brothel'
            
            # Wellness and relaxation
            elif properties.get('leisure') == 'sauna':
                feature_type = 'sauna'
            
            # Technology and innovation spaces
            elif properties.get('leisure') == 'hackerspace':
                feature_type = 'hackerspace'
            
            # Outdoor entertainment and sports
            elif properties.get('leisure') == 'miniature_golf':
                feature_type = 'miniature golf course'
            elif properties.get('leisure') == 'shooting_range':
                feature_type = 'shooting range'
            elif properties.get('leisure') == 'disc_golf':
                feature_type = 'disc golf course'
            elif properties.get('sport') == 'billiards':
                feature_type = 'billiards hall'
            elif properties.get('sport') == 'darts':
                feature_type = 'darts venue'
            elif properties.get('sport') == 'chess':
                feature_type = 'chess club'
            elif properties.get('sport') == 'go':
                feature_type = 'go club'
            elif properties.get('sport') == 'beachvolleyball':
                feature_type = 'beach volleyball court'
            
            # Outdoor facilities
            elif properties.get('leisure') == 'picnic_table':
                feature_type = 'picnic table'
            elif properties.get('leisure') == 'firepit':
                feature_type = 'fire pit'
            elif properties.get('leisure') == 'bbq':
                feature_type = 'barbecue area'
            elif properties.get('leisure') == 'bleachers':
                feature_type = 'bleachers'
            elif properties.get('leisure') == 'maze':
                feature_type = 'maze'
            
            # Educational and cultural attractions
            elif properties.get('amenity') == 'planetarium':
                feature_type = 'planetarium'
            elif properties.get('tourism') == 'theme_park':
                feature_type = 'theme park'
            elif properties.get('tourism') == 'aquarium':
                feature_type = 'aquarium'
            elif properties.get('tourism') == 'zoo':
                feature_type = 'zoo'
            
            # Retail entertainment
            elif properties.get('shop') == 'games':
                feature_type = 'game store'
            elif properties.get('shop') == 'video_games':
                feature_type = 'video game store'
            elif properties.get('shop') == 'music':
                feature_type = 'music store'
            elif properties.get('shop') == 'musical_instrument':
                feature_type = 'musical instrument shop'
            elif properties.get('shop') == 'video':
                feature_type = 'video store'
            elif properties.get('shop') == 'books':
                feature_type = 'bookstore'
            elif properties.get('shop') == 'art':
                feature_type = 'art store'
            elif properties.get('shop') == 'craft':
                feature_type = 'craft store'
            elif properties.get('shop') == 'hobby':
                feature_type = 'hobby shop'
            
            # Clubs and organizations
            elif properties.get('club') == 'sport':
                feature_type = 'sports club'
            elif properties.get('club') == 'social':
                feature_type = 'social club'
            elif properties.get('club') == 'veterans':
                feature_type = 'veterans club'
            elif properties.get('club') == 'youth':
                feature_type = 'youth club'
            elif properties.get('club') == 'senior':
                feature_type = 'senior center'
            elif properties.get('club') == 'community':
                feature_type = 'community club'
            elif properties.get('club') == 'photography':
                feature_type = 'photography club'
            elif properties.get('club') == 'computer':
                feature_type = 'computer club'
            elif properties.get('club') == 'automobile':
                feature_type = 'car club'
            
            # Craft and production
            elif properties.get('craft') == 'brewery':
                feature_type = 'brewery'
            elif properties.get('craft') == 'distillery':
                feature_type = 'distillery'
            elif properties.get('craft') == 'winery':
                feature_type = 'winery'
            
            # Animal-related entertainment
            elif properties.get('amenity') == 'game_feeding':
                feature_type = 'animal feeding area'
        
        # Advanced Accessibility Features - Comprehensive accessibility feature labeling
        elif (properties.get('tactile_paving') in ['yes', 'no'] or
              properties.get('traffic_signals:sound') == 'yes' or
              properties.get('traffic_signals:vibration') == 'yes' or
              properties.get('acoustic') == 'voice_description' or
              properties.get('braille') == 'yes' or
              properties.get('audio_loop') == 'yes' or
              properties.get('sign_language') == 'yes' or
              properties.get('toilets:wheelchair') in ['yes', 'no'] or
              properties.get('changing_table') in ['yes', 'no'] or
              properties.get('elevator') in ['yes', 'no'] or
              properties.get('escalator') in ['yes', 'no'] or
              properties.get('conveying') in ['yes', 'no'] or
              properties.get('automatic_door') in ['yes', 'no'] or
              'door:width' in properties or
              'kerb:height' in properties or
              'incline' in properties or
              properties.get('highway') in ['elevator', 'escalator'] or
              'wheelchair' in properties or
              properties.get('ramp') in ['yes', 'no'] or
              properties.get('ramp:wheelchair') in ['yes', 'no'] or
              properties.get('ramp:stroller') in ['yes', 'no'] or
              properties.get('ramp:bicycle') in ['yes', 'no'] or
              'step_count' in properties or
              properties.get('handrail') in ['yes', 'no'] or
              properties.get('handrail:center') in ['yes', 'no'] or
              properties.get('handrail:left') in ['yes', 'no'] or
              properties.get('handrail:right') in ['yes', 'no'] or
              'capacity:disabled' in properties or
              properties.get('parking:disabled') in ['yes', 'no'] or
              properties.get('priority') == 'disabled' or
              properties.get('bus:wheelchair') in ['yes', 'no'] or
              properties.get('subway:wheelchair') in ['yes', 'no'] or
              properties.get('tram:wheelchair') in ['yes', 'no'] or
              properties.get('train:wheelchair') in ['yes', 'no']):
            
            # Tactile navigation features
            if properties.get('tactile_paving') == 'yes':
                feature_type = 'tactile paving surface'
            elif properties.get('tactile_paving') == 'no':
                feature_type = 'no tactile paving'
            
            # Audio signal features
            elif properties.get('traffic_signals:sound') == 'yes':
                feature_type = 'audio traffic signal'
            elif properties.get('traffic_signals:vibration') == 'yes':
                feature_type = 'vibrating traffic signal'
            elif properties.get('acoustic') == 'voice_description':
                feature_type = 'voice description system'
            elif properties.get('audio_loop') == 'yes':
                feature_type = 'audio induction loop'
            
            # Visual and communication accessibility
            elif properties.get('braille') == 'yes':
                feature_type = 'braille signage'
            elif properties.get('sign_language') == 'yes':
                feature_type = 'sign language services'
            
            # Accessible toilet facilities
            elif properties.get('toilets:wheelchair') == 'yes':
                feature_type = 'wheelchair accessible toilet'
            elif properties.get('toilets:wheelchair') == 'no':
                feature_type = 'not wheelchair accessible toilet'
            elif properties.get('changing_table') == 'yes':
                feature_type = 'baby changing table'
            elif properties.get('changing_table') == 'no':
                feature_type = 'no baby changing table'
            
            # Vertical transport accessibility
            elif properties.get('elevator') == 'yes':
                feature_type = 'elevator available'
            elif properties.get('elevator') == 'no':
                feature_type = 'no elevator'
            elif properties.get('highway') == 'elevator':
                feature_type = 'elevator'
            elif properties.get('escalator') == 'yes':
                feature_type = 'escalator available'
            elif properties.get('escalator') == 'no':
                feature_type = 'no escalator'
            elif properties.get('highway') == 'escalator':
                feature_type = 'escalator'
            elif properties.get('conveying') == 'yes':
                feature_type = 'moving walkway available'
            elif properties.get('conveying') == 'no':
                feature_type = 'no moving walkway'
            
            # Door and entrance accessibility
            elif properties.get('automatic_door') == 'yes':
                feature_type = 'automatic door'
            elif properties.get('automatic_door') == 'no':
                feature_type = 'manual door'
            elif 'door:width' in properties:
                door_width = properties.get('door:width')
                feature_type = f'door width {door_width}'
            
            # Surface and path accessibility
            elif 'kerb:height' in properties:
                kerb_height = properties.get('kerb:height')
                feature_type = f'curb height {kerb_height}'
            elif 'incline' in properties:
                incline = properties.get('incline')
                feature_type = f'incline {incline}'
            
            # Wheelchair accessibility levels
            elif properties.get('wheelchair') == 'yes':
                feature_type = 'wheelchair accessible'
            elif properties.get('wheelchair') == 'no':
                feature_type = 'not wheelchair accessible'
            elif properties.get('wheelchair') == 'limited':
                feature_type = 'limited wheelchair access'
            elif properties.get('wheelchair') == 'designated':
                feature_type = 'designated wheelchair access'
            
            # Ramp accessibility
            elif properties.get('ramp') == 'yes':
                feature_type = 'ramp available'
            elif properties.get('ramp') == 'no':
                feature_type = 'no ramp'
            elif properties.get('ramp:wheelchair') == 'yes':
                feature_type = 'wheelchair ramp'
            elif properties.get('ramp:wheelchair') == 'no':
                feature_type = 'no wheelchair ramp'
            elif properties.get('ramp:stroller') == 'yes':
                feature_type = 'stroller ramp'
            elif properties.get('ramp:stroller') == 'no':
                feature_type = 'no stroller ramp'
            elif properties.get('ramp:bicycle') == 'yes':
                feature_type = 'bicycle ramp'
            elif properties.get('ramp:bicycle') == 'no':
                feature_type = 'no bicycle ramp'
            
            # Steps and barriers
            elif 'step_count' in properties:
                step_count = properties.get('step_count')
                feature_type = f'{step_count} steps'
            
            # Handrail support
            elif properties.get('handrail') == 'yes':
                feature_type = 'handrail available'
            elif properties.get('handrail') == 'no':
                feature_type = 'no handrail'
            elif properties.get('handrail:center') == 'yes':
                feature_type = 'center handrail'
            elif properties.get('handrail:left') == 'yes':
                feature_type = 'left handrail'
            elif properties.get('handrail:right') == 'yes':
                feature_type = 'right handrail'
            
            # Accessible parking and transport
            elif properties.get('parking:disabled') == 'yes':
                feature_type = 'accessible parking'
            elif properties.get('parking:disabled') == 'no':
                feature_type = 'no accessible parking'
            elif properties.get('priority') == 'disabled':
                feature_type = 'priority disabled access'
            elif 'capacity:disabled' in properties:
                capacity = properties.get('capacity:disabled')
                feature_type = f'accessible capacity {capacity}'
            
            # Public transport wheelchair accessibility
            elif properties.get('bus:wheelchair') == 'yes':
                feature_type = 'wheelchair accessible bus'
            elif properties.get('bus:wheelchair') == 'no':
                feature_type = 'not wheelchair accessible bus'
            elif properties.get('subway:wheelchair') == 'yes':
                feature_type = 'wheelchair accessible subway'
            elif properties.get('subway:wheelchair') == 'no':
                feature_type = 'not wheelchair accessible subway'
            elif properties.get('tram:wheelchair') == 'yes':
                feature_type = 'wheelchair accessible tram'
            elif properties.get('tram:wheelchair') == 'no':
                feature_type = 'not wheelchair accessible tram'
            elif properties.get('train:wheelchair') == 'yes':
                feature_type = 'wheelchair accessible train'
            elif properties.get('train:wheelchair') == 'no':
                feature_type = 'not wheelchair accessible train'
        
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