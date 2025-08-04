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
            'healthcare': [],
            'food_sustenance': [],
            'financial_services': [],
            'shopping_retail': [],
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
        
        # Healthcare facilities (amenity-based)
        if tags.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary']:
            self.features['healthcare'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id, 'healthcare_type': 'amenity'}
            })
        
        # Healthcare facilities (healthcare-based)
        elif tags.get('healthcare') in ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                                       'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                                       'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                                       'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                                       'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                                       'rehabilitation', 'sample_collection', 'speech_therapist',
                                       'vaccination_centre']:
            self.features['healthcare'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id, 'healthcare_type': 'healthcare'}
            })
        
        # Food & Sustenance establishments (amenity and shop-based)
        elif (tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten', 'nightclub'] or
              tags.get('shop') in ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer', 'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']):
            self.features['food_sustenance'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Financial Services establishments
        elif tags.get('amenity') in ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']:
            self.features['financial_services'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Shopping & Retail establishments (shop and amenity-based)
        elif (tags.get('shop') in ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 'variety_store', 'second_hand', 'charity', 'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor', 'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication', 'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo', 'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'appliance'] or
              tags.get('amenity') in ['marketplace', 'vending_machine']):
            self.features['shopping_retail'].append({
                'geometry': Point(n.location.lon, n.location.lat),
                'properties': {**tags, 'osm_id': n.id}
            })
        
        # Comprehensive Transit Infrastructure
        elif (tags.get('highway') in ['bus_stop', 'platform'] or
              tags.get('railway') in ['station', 'halt', 'platform', 'subway', 'tram', 'tram_stop', 'stop', 'subway_entrance'] or
              tags.get('public_transport') in ['platform', 'stop_position', 'station'] or
              tags.get('amenity') in ['bus_station', 'ferry_terminal'] or
              tags.get('aerialway') in ['station', 'loading_point'] or
              tags.get('aeroway') in ['terminal', 'gate']):
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
            
        # Water features (point features)
        elif (tags.get('amenity') in ['fountain', 'swimming_pool'] or
              tags.get('natural') in ['spring', 'hot_spring', 'geyser'] or
              tags.get('man_made') in ['water_tower', 'water_well', 'water_works', 'lighthouse'] or
              tags.get('leisure') in ['boat_sharing'] or
              tags.get('waterway') in ['waterfall', 'lock_gate', 'fuel']):
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
        
        # Transit Infrastructure (lines and areas)
        elif (tags.get('railway') in ['rail', 'subway', 'tram', 'light_rail', 'narrow_gauge', 'funicular', 'monorail'] or
              tags.get('highway') in ['bus_guideway'] or
              tags.get('aerialway') in ['cable_car', 'gondola', 'chair_lift', 'drag_lift', 'rope_tow', 'zip_line']):
            # These are linear transit infrastructure
            self.features['transit'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Transit Infrastructure (areas - stations, terminals, platforms)
        elif (tags.get('railway') in ['platform'] or
              tags.get('public_transport') in ['platform', 'station'] or
              tags.get('amenity') in ['bus_station', 'ferry_terminal'] or
              tags.get('aeroway') in ['terminal', 'runway', 'taxiway', 'aerodrome'] or
              tags.get('aerialway') in ['station']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['transit'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Linear platforms/infrastructure
                    self.features['transit'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Healthcare facilities (as areas/buildings)
        elif tags.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary'] or \
             tags.get('healthcare') in ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                                       'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                                       'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                                       'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                                       'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                                       'rehabilitation', 'sample_collection', 'speech_therapist',
                                       'vaccination_centre']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    healthcare_type = 'amenity' if tags.get('amenity') else 'healthcare'
                    self.features['healthcare'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id, 'healthcare_type': healthcare_type}
                    })
            except Exception:
                pass
        
        # Food & Sustenance establishments (as areas/buildings)
        elif (tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten', 'nightclub'] or
              tags.get('shop') in ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer', 'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['food_sustenance'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Financial Services establishments (as areas/buildings)
        elif tags.get('amenity') in ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['financial_services'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Shopping & Retail establishments (as areas/buildings)
        elif (tags.get('shop') in ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 'variety_store', 'second_hand', 'charity', 'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor', 'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication', 'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo', 'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'appliance'] or
              tags.get('amenity') in ['marketplace', 'vending_machine']):
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['shopping_retail'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
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
        
        # Linear Water Features (waterways)
        elif tags.get('waterway') in ['river', 'stream', 'canal', 'drain', 'ditch', 'rapids', 'dam', 'weir', 'dock', 'boatyard']:
            self.features['water'].append({
                'geometry': line,
                'properties': {**tags, 'osm_id': w.id}
            })
        
        # Water areas - Natural water bodies
        elif tags.get('natural') in ['water', 'coastline', 'beach', 'bay', 'strait', 'shoal', 'reef', 'wetland']:
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
        
        # Man-made Water Features (areas and lines)
        elif tags.get('man_made') in ['reservoir', 'pier', 'breakwater', 'groyne', 'floating_dock']:
            try:
                if w.is_closed() and tags.get('man_made') in ['reservoir']:
                    # Area features
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Linear features (piers, breakwaters, etc.)
                    self.features['water'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Leisure Water Areas
        elif tags.get('leisure') in ['swimming_pool', 'water_park', 'marina', 'slipway']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
                else:
                    # Linear slipways
                    self.features['water'].append({
                        'geometry': line,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Landuse Water Areas
        elif tags.get('landuse') in ['reservoir', 'salt_pond', 'aquaculture', 'basin']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass
        
        # Amenity Water Areas
        elif tags.get('amenity') in ['swimming_pool']:
            try:
                if w.is_closed():
                    geom = wkb.create_polygon(w)
                    poly = loads(geom, hex=True)
                    self.features['water'].append({
                        'geometry': poly,
                        'properties': {**tags, 'osm_id': w.id}
                    })
            except Exception:
                pass

    def area(self, a):
        """Process area/relation features"""
        tags = {t.k: t.v for t in a.tags}
        
        try:
            wkb = osmium.geom.WKBFactory()
            
            # Healthcare facilities (as relations)
            if tags.get('amenity') in ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'veterinary'] or \
               tags.get('healthcare') in ['alternative', 'audiologist', 'birthing_centre', 'blood_bank', 
                                         'blood_donation', 'centre', 'clinic', 'counselling', 'dentist',
                                         'dialysis', 'doctor', 'hospice', 'hospital', 'laboratory',
                                         'midwife', 'nurse', 'occupational_therapist', 'optometrist',
                                         'pharmacy', 'physiotherapist', 'podiatrist', 'psychotherapist',
                                         'rehabilitation', 'sample_collection', 'speech_therapist',
                                         'vaccination_centre']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if healthcare area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        healthcare_type = 'amenity' if tags.get('amenity') else 'healthcare'
                        self.features['healthcare'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id, 'healthcare_type': healthcare_type}
                        })
                except Exception:
                    pass
            
            # Food & Sustenance establishments (as relations)
            elif (tags.get('amenity') in ['restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten', 'nightclub'] or
                  tags.get('shop') in ['alcohol', 'bakery', 'beverages', 'butcher', 'cheese', 'chocolate', 'coffee', 'confectionery', 'convenience', 'deli', 'farm', 'frozen_food', 'greengrocer', 'health_food', 'nuts', 'pastry', 'seafood', 'tea', 'wine', 'supermarket']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if food establishment area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['food_sustenance'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Financial Services establishments (as relations)
            elif tags.get('amenity') in ['bank', 'atm', 'post_office', 'bureau_de_change', 'money_transfer', 'payment_centre']:
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if financial services area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['financial_services'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Shopping & Retail establishments (as relations)
            elif (tags.get('shop') in ['department_store', 'general', 'kiosk', 'mall', 'supermarket', 'wholesale', 'variety_store', 'second_hand', 'charity', 'clothes', 'shoes', 'bag', 'boutique', 'fabric', 'jewelry', 'leather', 'watches', 'tailor', 'computer', 'electronics', 'mobile_phone', 'hifi', 'telecommunication', 'beauty', 'chemist', 'cosmetics', 'hairdresser', 'massage', 'optician', 'perfumery', 'tattoo', 'furniture', 'garden_centre', 'hardware', 'doityourself', 'florist', 'appliance'] or
                  tags.get('amenity') in ['marketplace', 'vending_machine']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if shopping/retail area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['shopping_retail'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Transit Infrastructure (as relations)
            elif (tags.get('railway') in ['station', 'platform'] or 
                  tags.get('public_transport') in ['platform', 'station'] or 
                  tags.get('amenity') in ['bus_station', 'ferry_terminal'] or 
                  tags.get('aeroway') in ['terminal', 'aerodrome'] or 
                  tags.get('aerialway') in ['station']):
                try:
                    geom = wkb.create_multipolygon(a)
                    poly = loads(geom, hex=True)
                    
                    # Check if transit area intersects with bounds
                    bounds_poly = Polygon([
                        (self.bounds['west'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['south']),
                        (self.bounds['east'], self.bounds['north']),
                        (self.bounds['west'], self.bounds['north'])
                    ])
                    
                    if poly.intersects(bounds_poly):
                        self.features['transit'].append({
                            'geometry': poly,
                            'properties': {**tags, 'osm_id': a.id}
                        })
                except Exception:
                    pass
            
            # Buildings
            elif 'building' in tags:
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
            
            # Water areas - comprehensive coverage
            elif (tags.get('natural') in ['water', 'beach', 'bay', 'strait', 'shoal', 'reef', 'wetland'] or
                  tags.get('man_made') in ['reservoir', 'water_works'] or
                  tags.get('leisure') in ['swimming_pool', 'water_park', 'marina'] or
                  tags.get('landuse') in ['reservoir', 'salt_pond', 'aquaculture', 'basin'] or
                  tags.get('amenity') in ['swimming_pool']):
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