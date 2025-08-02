"""OSM data processor ported from original osm_tile_processor.py"""

import osmium
from shapely.geometry import Point, LineString, Polygon
from shapely.wkb import loads

class OSMHandler(osmium.SimpleHandler):
    """OSM data handler for extracting features from OSM data."""
    
    def __init__(self, bounds):
        super().__init__()
        self.bounds = bounds
        self.features = {
            'buildings': [],
            'roads': [],
            'accessibility': [],
            'pedestrian_areas': [],
            'transit': [],
            'water': [],
            'parks': [],
            'landuse': [],
            'vegetation': [],
            'religious': [],
            'parking': [],
            'sensory_accessibility': [],
            'accessible_facilities': [],
            'mobility_access': [],
            'accessible_transport': []
        }
        
    def is_in_bounds(self, lat, lon):
        """Check if coordinate is within tile bounds"""
        return (self.bounds['south'] <= lat <= self.bounds['north'] and
                self.bounds['west'] <= lon <= self.bounds['east'])
    
    def node(self, n):
        """Process node features"""
        if not self.is_in_bounds(n.location.lat, n.location.lon):
            return
            
        tags = {t.k: t.v for t in n.tags}
        
        # Transit stops
        if tags.get('highway') == 'bus_stop' or tags.get('railway') in ['station', 'subway_entrance']:
            self.features['transit'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Accessibility features
        if tags.get('amenity') == 'parking' and tags.get('wheelchair') == 'yes':
            self.features['accessibility'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Water features (fountains)
        if tags.get('amenity') == 'fountain':
            self.features['water'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Park amenities (playgrounds)
        if tags.get('amenity') == 'playground':
            self.features['parks'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Individual trees
        if tags.get('natural') == 'tree':
            self.features['vegetation'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Religious places (nodes)
        if tags.get('amenity') == 'place_of_worship':
            self.features['religious'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Parking (nodes - bicycle/motorcycle parking stands)
        if tags.get('amenity') in ['parking', 'bicycle_parking', 'motorcycle_parking']:
            # Skip if it's wheelchair parking (handled by accessibility)
            if not (tags.get('amenity') == 'parking' and tags.get('wheelchair') == 'yes'):
                self.features['parking'].append({
                    'geometry': Point(n.location.lon, n.location.lat),
                    'properties': {**tags, 'osm_id': n.id}
                })
        
        # Sensory accessibility features
        if (tags.get('tactile_paving') in ['yes', 'no'] or
            tags.get('traffic_signals:sound') == 'yes' or
            tags.get('traffic_signals:vibration') == 'yes' or
            tags.get('acoustic') == 'voice_description' or
            tags.get('braille') == 'yes' or
            tags.get('audio_loop') == 'yes' or
            tags.get('sign_language') == 'yes'):
            self.features['sensory_accessibility'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Accessible facilities features
        if (tags.get('toilets:wheelchair') in ['yes', 'no'] or
            tags.get('changing_table') in ['yes', 'no'] or
            tags.get('elevator') in ['yes', 'no'] or
            tags.get('escalator') in ['yes', 'no'] or
            tags.get('conveying') in ['yes', 'no'] or
            tags.get('automatic_door') in ['yes', 'no'] or
            'door:width' in tags or
            'kerb:height' in tags or
            'incline' in tags or
            tags.get('highway') == 'elevator' or
            tags.get('highway') == 'escalator'):
            self.features['accessible_facilities'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Mobility access features
        if ('wheelchair' in tags or
            tags.get('ramp') == 'yes' or
            tags.get('ramp:wheelchair') == 'yes' or
            tags.get('ramp:stroller') == 'yes' or
            tags.get('ramp:bicycle') == 'yes' or
            'step_count' in tags or
            tags.get('handrail') == 'yes' or
            tags.get('handrail:center') == 'yes' or
            tags.get('handrail:left') == 'yes' or
            tags.get('handrail:right') == 'yes'):
            self.features['mobility_access'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
            
        # Accessible transport features
        if ('capacity:disabled' in tags or
            tags.get('parking:disabled') == 'yes' or
            tags.get('priority') == 'disabled' or
            tags.get('bus:wheelchair') == 'yes' or
            tags.get('subway:wheelchair') == 'yes' or
            tags.get('tram:wheelchair') == 'yes' or
            tags.get('train:wheelchair') == 'yes'):
            self.features['accessible_transport'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
    
    def way(self, w):
        """Process way features"""
        if len(w.nodes) < 2:
            return
            
        # Get node locations
        try:
            wkb = osmium.geom.WKBFactory()
            geom = wkb.create_linestring(w)
            line = loads(geom, hex=True)
            
            # Check if the line intersects with the tile bounds
            # A line can pass through a tile even if no nodes are within it
            tile_bounds = (self.bounds['west'], self.bounds['south'], 
                          self.bounds['east'], self.bounds['north'])
            line_bounds = line.bounds  # (minx, miny, maxx, maxy)
            
            # Check if bounding boxes overlap
            if not (line_bounds[0] <= tile_bounds[2] and line_bounds[2] >= tile_bounds[0] and
                    line_bounds[1] <= tile_bounds[3] and line_bounds[3] >= tile_bounds[1]):
                return
                
        except Exception:
            return
        
        tags = {t.k: t.v for t in w.tags}
        
        # Buildings
        if 'building' in tags:
            try:
                # Try to create polygon if closed way
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['buildings'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Roads
        elif tags.get('highway') in ['motorway', 'trunk', 'primary', 'secondary', 
                                      'tertiary', 'residential', 'service', 'unclassified',
                                      'pedestrian', 'footway', 'cycleway', 'path', 
                                      'living_street', 'track', 'bus_guideway', 'escape',
                                      'raceway', 'road', 'busway', 'motorway_link', 
                                      'trunk_link', 'primary_link', 'secondary_link', 
                                      'tertiary_link', 'bridleway', 'steps', 'corridor', 'sidewalk']:
            self.features['roads'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Water features (rivers, streams, etc.)
        elif tags.get('waterway') in ['river', 'stream', 'canal', 'drain', 'ditch']:
            self.features['water'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Parks and leisure areas
        elif tags.get('leisure') in ['park', 'garden', 'playground', 'dog_park', 'nature_reserve'] or \
             tags.get('landuse') in ['grass', 'recreation_ground', 'village_green']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['parks'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Water areas
        elif tags.get('natural') in ['water', 'coastline', 'beach', 'bay', 'strait']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Coastlines are lines
                    self.features['water'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass

    def area(self, a):
        """Process area/relation features"""
        tags = {t.k: t.v for t in a.tags}
        
        try:
            wkb = osmium.geom.WKBFactory()
            
            # Buildings
            if 'building' in tags:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['buildings'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Parks and leisure areas
            elif tags.get('leisure') in ['park', 'garden', 'playground', 'dog_park', 'nature_reserve'] or \
                 tags.get('landuse') in ['grass', 'recreation_ground', 'village_green']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['parks'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Water areas
            elif tags.get('natural') in ['water', 'beach', 'bay']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['water'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
                    
        except Exception:
            pass